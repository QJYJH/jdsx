"""候选人的备注数据访问"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class NoteStore:
    """数据管理"""

    def __init__(self,db_path:str = "./data/candidates.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()

    def _init_database(self):
        """初始化表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS candidate_notes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                note_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
                         )
            """)

            # 创建索引
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_candidate_notes
                ON candidate_notes(candidate_id,created_at DESC)
                """
            )
    
    def add_note(self,candidate_id: int, content:str) -> bool:
        """添加备注"""
        if not content or not content.strip():
            return False

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO candidate_notes (candidate_id, note_content) VALUES (?, ?)",
                (candidate_id, content.strip())
            )
            return True
        
    def get_notes(self, candidate_id:int, limit:int = None) -> List[Dict[str,Any]]:
        """获取候选人备注（按时间倒序）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            sql = """
                SELECT id, note_content, created_at
                FROM candidate_notes
                WHERE candidate_id = ?
                ORDER BY created_at DESC
                """
            
            if limit:
                sql += f" LIMIT {limit}"
            
            cursor = conn.execute(sql, (candidate_id,))

            notes = []
            for row in cursor.fetchall():
                notes.append({
                    'id': row['id'],
                    'content': row['note_content'],
                    'created_at': row['created_at']
                })
            
            return notes
        
    def delete_note(self, note_id:int) -> bool:
        """删除"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM candidate_notes WHERE id = ?", (note_id,))
            return cursor.rowcount > 0
        
    def get_note_count(self,candidate_id: int) -> int:
        """候选人备注数量"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM candidate_notes WHERE candidate_id = ?",
                (candidate_id,)
            )
            return cursor.fetchone()[0]
        


