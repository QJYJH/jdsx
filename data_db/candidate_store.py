"""候选人数据访问层"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..data_model.candidate import CandidateProfile
from ..data_model.ana_model import ResumeAnalysis

class CandidateStore:
    """候选人数据存储管理"""
    def __init__(self, db_path: str = './data/candidates.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    position_id INTEGER NOT NULL,
                    file_name TEXT NOT NULL,
                    original_file_path TEXT,
                        
                    
                    -- 基础档案
                    total_years_experience INTEGER,
                    profile_json TEXT,
                        
                    -- AI分析结果
                    recommendation_level TEXT DEFAULT '可考虑',
                    ai_atrengths TEXT,
                    ai_concerns TEXT,
                    ai_summary TEXT,
                        

                    -- HR标签
                    hr_tag TEXT DEFAULT NULL,
                    hr_note TEXT DEFAULT NULL,
                    hr_tagged_at TIMESTAMP,
                        
                    -- 解析状态
                    parser_status TEXT DEFAULT 'success',
                    error_message TEXT,
                        
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                """)
            
        try:
            conn.execute("ALTER TABLE candidates ADD COLUMN original_file_path TEXT")
        except sqlite3.OperationalError:
            pass

        # 创建索引
        conn.execute("CREATE INDEX IF NOT EXISTS idx_position_id ON candidates(position_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_position_hr_tag ON candidates(position_id, hr_tag)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_position_recommendation ON candidates(position_id, recommendation_level)")

        # 创建触发器
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS update_candidates_timestamp
            AFTER UPDATE ON candidates
            BEGIN
                UPDATE candidates SET updated_at = CURRENT_TIMESTAMP WHER id = NEW.id;
            END
            """)
            
    def save(self, profile: CandidateProfile, analysis: ResumeAnalysis = None, original_file_path: str = None) -> int:
        """保存候选人的档案（AI分析结果）"""
        with sqlite3.connect(self.db_path) as conn:
            # 如果有AI分析结果，更新profile
            if analysis:
                profile