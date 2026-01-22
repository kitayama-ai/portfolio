import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import json
import hashlib
from openai import OpenAI
from config import Config
import os

class ExcelProcessor:
    """Excel/CSV教材の処理とベクトル化"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
        self.data_dir = Config.PDF_STORAGE_DIR  # 既存のディレクトリ構造を再利用
        self.vector_dir = Config.VECTOR_STORAGE_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_excel(self, file_path: str) -> str:
        """Excelファイルからテキストを抽出"""
        try:
            # Excelファイルを読み込み
            excel_file = pd.ExcelFile(file_path)
            text_parts = []
            
            # 各シートを処理
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                text_parts.append(f"シート名: {sheet_name}\n")
                # データフレームをテキスト形式に変換
                text_parts.append(df.to_string(index=False))
                text_parts.append("\n\n")
            
            return "\n".join(text_parts).strip()
        except Exception as e:
            raise Exception(f"Excel抽出失敗: {str(e)}")
    
    def extract_text_from_csv(self, file_path: str) -> str:
        """CSVファイルからテキストを抽出"""
        try:
            # エンコーディングを自動検出
            encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp', 'latin-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("CSVファイルのエンコーディングを検出できませんでした")
            
            # データフレームをテキスト形式に変換
            return df.to_string(index=False)
        except Exception as e:
            raise Exception(f"CSV抽出失敗: {str(e)}")
    
    def split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """テキストをチャンクに分割（PDFProcessorと同じロジック）"""
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # オーバーラップ
                overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_words + [word]
                current_length = sum(len(w) + 1 for w in current_chunk)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """テキストのベクトル化（PDFProcessorと同じロジック）"""
        if not self.client:
            raise Exception("OpenAI APIキーが設定されていません")
        
        embeddings = []
        # バッチ処理（最大100件ずつ）
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            try:
                response = self.client.embeddings.create(
                    model=Config.EMBEDDING_MODEL,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                print(f"埋め込み生成エラー: {e}")
                raise
        
        return embeddings
    
    def process_file(self, file_path: str, course_id: str, file_type: str) -> Dict:
        """Excel/CSVファイルを処理してベクトル化し、保存"""
        # ファイルをコースごとのディレクトリに保存
        course_data_dir = self.data_dir / course_id
        course_data_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイルをコピー
        source_file = Path(file_path)
        saved_path = course_data_dir / source_file.name
        import shutil
        shutil.copy2(file_path, saved_path)
        
        # ファイルタイプに応じてテキスト抽出
        if file_type == "excel":
            text = self.extract_text_from_excel(str(saved_path))
        elif file_type == "csv":
            text = self.extract_text_from_csv(str(saved_path))
        else:
            raise Exception(f"サポートされていないファイルタイプ: {file_type}")
        
        # チャンク分割
        chunks = self.split_text(text)
        
        # ベクトル化
        embeddings = self.create_embeddings(chunks)
        
        # メタデータとベクトルを保存
        vector_file = self.vector_dir / f"{course_id}_{saved_path.stem}_{file_type}.json"
        data = {
            "course_id": course_id,
            "file_path": str(saved_path),
            "file_type": file_type,
            "chunks": chunks,
            "embeddings": embeddings,
            "metadata": {
                "filename": source_file.name,
                "chunk_count": len(chunks),
                "total_text_length": len(text)
            }
        }
        
        with open(vector_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            "course_id": course_id,
            "file_path": str(saved_path),
            "vector_file": str(vector_file),
            "chunk_count": len(chunks),
            "text_length": len(text),
            "file_type": file_type
        }
    
    def load_vectors(self, course_id: str, file_type: Optional[str] = None) -> Optional[Dict]:
        """コースのベクトルデータを読み込み"""
        if file_type:
            pattern = f"{course_id}_*_{file_type}.json"
        else:
            pattern = f"{course_id}_*.json"
        
        vector_files = list(self.vector_dir.glob(pattern))
        if not vector_files:
            return None
        
        # 最新のファイルを読み込み
        latest_file = max(vector_files, key=lambda p: p.stat().st_mtime)
        with open(latest_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def search_similar_chunks(self, query_embedding: List[float], course_id: str, top_k: int = 5) -> List[Dict]:
        """類似チャンクを検索（PDFProcessorと同じロジック）"""
        vector_data = self.load_vectors(course_id)
        if not vector_data:
            return []
        
        chunks = vector_data["chunks"]
        embeddings = vector_data["embeddings"]
        
        # コサイン類似度を計算
        import numpy as np
        
        query_vec = np.array(query_embedding)
        similarities = []
        
        for i, emb in enumerate(embeddings):
            emb_vec = np.array(emb)
            # コサイン類似度
            similarity = np.dot(query_vec, emb_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(emb_vec))
            similarities.append((similarity, i, chunks[i]))
        
        # 上位k件を返す
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [
            {
                "chunk": chunk,
                "similarity": float(sim),
                "index": idx
            }
            for sim, idx, chunk in similarities[:top_k]
        ]
