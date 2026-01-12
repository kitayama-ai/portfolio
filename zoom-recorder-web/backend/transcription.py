from openai import OpenAI
from config import Config
import os

class TranscriptionService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
        self.model = Config.WHISPER_MODEL
    
    def transcribe_audio(self, audio_file_path, language="ja"):
        """
        音声ファイルを文字起こし
        language="ja"で日本語に最適化
        """
        if not self.client:
            raise Exception("OpenAI APIキーが設定されていません")
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )
            
            return {
                "text": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration
            }
        except Exception as e:
            raise Exception(f"文字起こしエラー: {str(e)}")
    
    def check_file_size(self, file_path):
        """ファイルサイズをチェック（25MB制限）"""
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > Config.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"ファイルサイズが大きすぎます: {size_mb:.2f}MB "
                f"(上限: {Config.MAX_FILE_SIZE_MB}MB)"
            )
        return size_mb
