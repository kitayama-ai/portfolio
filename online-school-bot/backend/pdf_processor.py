import PyPDF2
import pdfplumber
from pathlib import Path
from typing import List, Dict, Optional
import json
import hashlib
from openai import OpenAI
from config import Config
import os

class PDFProcessor:
    """PDF教材の処理とベクトル化"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
        self.pdf_dir = Config.PDF_STORAGE_DIR
        self.vector_dir = Config.VECTOR_STORAGE_DIR
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text(self, pdf_path: str) -> str:
        """PDFからテキストを抽出"""
        text = ""
        try:
            # pdfplumberで試行（より高精度）
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumberでエラー: {e}, PyPDF2で再試行")
            # PyPDF2でフォールバック
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                print(f"PyPDF2でもエラー: {e2}")
                raise Exception(f"PDF抽出失敗: {str(e2)}")
        
        return text.strip()
    
    def split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """テキストをチャンクに分割"""
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
        """テキストのベクトル化"""
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
    
    def process_pdf(self, pdf_path: str, course_id: str) -> Dict:
        """PDFを処理してベクトル化し、保存"""
        # PDFをコースごとのディレクトリに保存
        course_pdf_dir = self.pdf_dir / course_id
        course_pdf_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイルをコピー
        pdf_file = Path(pdf_path)
        saved_path = course_pdf_dir / pdf_file.name
        import shutil
        shutil.copy2(pdf_path, saved_path)
        
        # テキスト抽出
        text = self.extract_text(str(saved_path))
        
        # チャンク分割
        chunks = self.split_text(text)
        
        # ベクトル化
        embeddings = self.create_embeddings(chunks)
        
        # メタデータとベクトルを保存
        vector_file = self.vector_dir / f"{course_id}_{saved_path.stem}.json"
        data = {
            "course_id": course_id,
            "pdf_path": str(saved_path),
            "chunks": chunks,
            "embeddings": embeddings,
            "metadata": {
                "filename": pdf_file.name,
                "chunk_count": len(chunks),
                "total_text_length": len(text)
            }
        }
        
        with open(vector_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            "course_id": course_id,
            "pdf_path": str(saved_path),
            "vector_file": str(vector_file),
            "chunk_count": len(chunks),
            "text_length": len(text)
        }
    
    def load_vectors(self, course_id: str) -> Optional[Dict]:
        """コースのベクトルデータを読み込み"""
        vector_files = list(self.vector_dir.glob(f"{course_id}_*.json"))
        if not vector_files:
            return None
        
        # 最新のファイルを読み込み
        latest_file = max(vector_files, key=lambda p: p.stat().st_mtime)
        with open(latest_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def search_similar_chunks(self, query_embedding: List[float], course_id: str, top_k: int = 5) -> List[Dict]:
        """類似チャンクを検索"""
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
