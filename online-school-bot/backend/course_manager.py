from pathlib import Path
from typing import Dict, List, Optional
import json
from config import Config

class CourseManager:
    """コース管理（コースIDと担当者のマッピング）"""
    
    def __init__(self):
        self.config_file = Config.CONFIG_FILE
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.courses = self._load_courses()
    
    def _load_courses(self) -> Dict:
        """コース設定を読み込み"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_courses(self):
        """コース設定を保存"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.courses, f, ensure_ascii=False, indent=2)
    
    def register_course(self, course_id: str, course_name: str, 
                       manager_slack_id: Optional[str] = None,
                       platform: str = "chatwork") -> bool:
        """コースを登録"""
        if course_id not in self.courses:
            self.courses[course_id] = {
                "course_id": course_id,
                "course_name": course_name,
                "manager_slack_id": manager_slack_id,
                "platform": platform,  # "chatwork" or "line"
                "created_at": json.dumps(Path(__file__).stat().st_mtime)
            }
            self._save_courses()
            return True
        return False
    
    def update_course_platform(self, course_id: str, platform: str) -> bool:
        """コースのプラットフォームを更新"""
        if course_id in self.courses:
            self.courses[course_id]["platform"] = platform
            self._save_courses()
            return True
        return False
    
    def get_course(self, course_id: str) -> Optional[Dict]:
        """コース情報を取得"""
        return self.courses.get(course_id)
    
    def get_all_courses(self) -> List[Dict]:
        """全コースを取得"""
        return list(self.courses.values())
    
    def update_course_manager(self, course_id: str, manager_slack_id: str) -> bool:
        """コース担当者を更新"""
        if course_id in self.courses:
            self.courses[course_id]["manager_slack_id"] = manager_slack_id
            self._save_courses()
            return True
        return False
