from openai import OpenAI
from config import Config
from pdf_processor import PDFProcessor
from excel_processor import ExcelProcessor
from spreadsheet import SpreadsheetService
from typing import List, Dict, Optional
import json

class AIResponder:
    """AI回答生成（教材内容 + ネット検索）"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
        try:
            self.pdf_processor = PDFProcessor()
        except:
            self.pdf_processor = None
        try:
            self.excel_processor = ExcelProcessor()
        except:
            self.excel_processor = None
        try:
            self.spreadsheet_service = SpreadsheetService()
        except:
            self.spreadsheet_service = None
    
    def search_web(self, query: str) -> Optional[str]:
        """ネット検索（OpenAIの関数呼び出し機能を使用）"""
        # 注意: 実際のネット検索には外部API（SerpAPI、Google Custom Search等）が必要
        # ここでは簡易的にOpenAIに検索を依頼する形式
        # 本番環境では適切な検索APIを統合してください
        
        # フォールバック: 検索結果なしとして処理
        return None
    
    def generate_response(self, user_message: str, course_id: str, conversation_history: List[Dict] = None) -> str:
        """回答を生成"""
        if not self.client:
            return "申し訳ございません。AIサービスが利用できません。"
        
        # 教材から関連情報を検索（PDF、Excel、CSV、スプレッドシートすべてから）
        relevant_chunks = []
        try:
            # ユーザーの質問をベクトル化
            query_embedding = self.client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=[user_message]
            ).data[0].embedding
            
            # PDFから検索
            if self.pdf_processor:
                try:
                    similar_chunks = self.pdf_processor.search_similar_chunks(
                        query_embedding, course_id, top_k=5
                    )
                    relevant_chunks.extend([chunk["chunk"] for chunk in similar_chunks if chunk["similarity"] > 0.7])
                except Exception as e:
                    print(f"PDF検索エラー: {e}")
            
            # Excel/CSVから検索
            if self.excel_processor:
                try:
                    similar_chunks = self.excel_processor.search_similar_chunks(
                        query_embedding, course_id, top_k=5
                    )
                    relevant_chunks.extend([chunk["chunk"] for chunk in similar_chunks if chunk["similarity"] > 0.7])
                except Exception as e:
                    print(f"Excel/CSV検索エラー: {e}")
            
            # スプレッドシートから検索（リアルタイム読み込み）
            if self.excel_processor:
                try:
                    # スプレッドシートのベクトルファイルを検索
                    from pathlib import Path
                    vector_dir = Config.VECTOR_STORAGE_DIR
                    spreadsheet_files = list(vector_dir.glob(f"{course_id}_spreadsheet_*.json"))
                    
                    for spreadsheet_file in spreadsheet_files:
                        with open(spreadsheet_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if "embeddings" in data and "chunks" in data:
                                # コサイン類似度を計算
                                import numpy as np
                                query_vec = np.array(query_embedding)
                                similarities = []
                                
                                for i, emb in enumerate(data["embeddings"]):
                                    emb_vec = np.array(emb)
                                    similarity = np.dot(query_vec, emb_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(emb_vec))
                                    if similarity > 0.7:
                                        similarities.append((similarity, i, data["chunks"][i]))
                                
                                similarities.sort(reverse=True, key=lambda x: x[0])
                                relevant_chunks.extend([chunk for _, _, chunk in similarities[:5]])
                except Exception as e:
                    print(f"スプレッドシート検索エラー: {e}")
                    
        except Exception as e:
            print(f"教材検索エラー: {e}")
        
        # 会話履歴を準備
        messages = [
            {
                "role": "system",
                "content": f"""あなたはオンラインスクールの教材内容に関する質問に答える親切なアシスタントです。
教材の内容に基づいて正確に回答してください。教材に記載がない場合は、一般的な知識や最新情報を参照して回答できます。

重要なルール:
- 教材の内容を優先して回答する
- 教材にない情報は「教材には記載がありませんが、一般的には...」と前置きする
- 専門用語は分かりやすく説明する
- 具体例を交えて説明する
- 回答は簡潔で分かりやすく"""
            }
        ]
        
        # 会話履歴を追加（直近10件）
        if conversation_history:
            recent_history = conversation_history[-10:]
            for msg in recent_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # 教材の関連情報を追加
        if relevant_chunks:
            context = "\n\n【教材の関連内容】\n" + "\n\n".join(relevant_chunks[:3])
            messages[-1]["content"] = f"{messages[-1]['content']}\n\n{context}"
        
        # 回答生成
        try:
            response = self.client.chat.completions.create(
                model=Config.GPT_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # ネット検索が必要な場合（教材に情報がない場合）
            if not relevant_chunks or len(relevant_chunks) == 0:
                # 一般的な知識として回答（実際のネット検索APIを統合する場合はここで呼び出す）
                pass
            
            return answer
        
        except Exception as e:
            print(f"回答生成エラー: {e}")
            return "申し訳ございません。回答の生成中にエラーが発生しました。しばらくしてから再度お試しください。"
