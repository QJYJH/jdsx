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
                profile.recommendation_level = analysis.recommendation_level
                profile.ai_strengths = analysis.key_strengths
                profile.ai_concerns = analysis.key_concerns
                profile.ai_summary = analysis.one_sentence_summary

            cursor = conn.execute(
                """
                INSERT INTO candidates(
                    name, position_id, file_name, original_file_path,
                    total_years_experience, profile_json,
                    recommendation_level, ai_strengths, ai_concerns, ai_summary,
                    parser_status, error_message
                )VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.name,
                    profile.position_id,
                    profile.file_name,
                    original_file_path,
                    profile.total_years_experience,
                    profile.model_dump_json,
                    profile.recommendation_level,
                    json.dumps(profile.ai_strengths,ensure_ascii=False),
                    json.dumps(profile.ai_concerns,ensure_ascii=False),
                    profile.ai_summary,
                    profile.parser_status,
                    profile.error_message
                )
            )
            return cursor.lastrowid
        
    def get_by_id(self, candidate_id: int) -> Optional[CandidateProfile]:
        """根据id获取候选人"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT *FROM candidates WHERE id = ?",(candidate_id,))
            row = cursor.fetchone()
            if row and row['profile_json']:
                return CandidateProfile.model_validate_json(row['profile_json'])
        return None

    def get_by_position(self, position_id:int,sort_by:str = 'tag_priority') -> List[Dict[str,Any]]:
        """获取岗位的候选人列表（'tag_priority','recommendation','time'）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # 排序sql
            if sort_by == "tag_priority":
                order_clause = """
                    ORDER BY
                        CASE hr_tag
                            WHEN 'star' THEN 1
                            WHEN 'interview' THEN 2
                            WHEN 'pending' THEN 3
                            WHEN NULL then 4
                            WHEN 'rejected' THEN 5
                            ELSE 6
                        END,
                        CASE recommendation_level
                            WHEN '强烈推荐' THEN 1
                            WHEN '推荐' THEN 2
                            WHEN '可考虑' THEN 3
                            WHEN '不推荐' THEN 4
                            ELSE 5
                        END,
                        created_at DESC
                    """
            
            elif sort_by == "recommendation":
                order_clause = """
                    ORDER BY
                        CASE recommendation_level
                            WHEN '强烈推荐' THEN 1
                            WHEN '推荐' THEN 2
                            WHEN '可考虑' THEN 3
                            WHEN '不推荐' THEN 4
                            ELSE 5
                        END,
                        created_at DESC
                """
            
            else: # time
                order_clause = "ORDER BY created_at DESC"
            
            cursor = conn.execute(
                f"""
                SELECT 
                    id, name, file_name, original_file_path,
                    recommendation_level,
                    ai_strengths, ai_concerns, ai_summary,
                    hr_tag, hr_note, hr_tagged_at,
                    parser_status, error_message,
                    profile_json,
                    created_at
                FROM candidates
                WHERE position_id = ?
                {order_clause}
                """,
                (position_id,)
            )

            results = []
            for row in cursor.fetchall():
                data = dict(row)
                # 解析json字段
                data['ai_strengths'] = json.loads(data["ai_strengths"]) if data["ai_strengths"] else []
                data["ai_concerns"] = json.loads(data["ai_concerns"]) if data["ai_concerns"] else []

                if data.get("profile_json"):
                    try:
                        profile = json.loads(data['profile_json'])
                        data['work_experience'] = profile.get("work_experience", [])
                        data['project_experience'] = profile.get('project_experience',[])
                    except:
                        data['work_experience'] = []
                        data['project_experience'] = []
                else:
                    data['work_experience'] = []
                    data['project_experience'] = []
                
                results.append(data)
                
            return results
            
    def update_hr_tag(self, candidate_id:int, tag:str = None, note:str = None) ->bool:
        """更新hr标签和标注"""
        updates = []
        params = []

        if tag is not None:
            updates.append("hr_tag = ?")
            params.append(tag)
            updates.append("hr_tagged_at = CURRENT_TIMESTAMP")

            if note is not None:
                updates.append("hr_note = ?")
                params.append(note)
            
            if not updates:
                return False
            
            params.append(candidate_id)
            sql = f"UPDATE candidates SET {', '.join(updates)} WHERE id = ?"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(sql,params)
                return cursor.rowcount > 0
            
    def delete(self, candidate_id: int) -> bool:
        """删除候选人"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM candidates WHERE id =?", (candidate_id,))
            return cursor.rowcount > 0
        
    def get_stats_by_position(self,position_id:int) -> Dict[str,int]:
        """获取岗位候选人的统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN hr_tag = 'star' THEN 1 ELSE 0 END) as star_count,
                SUM(CASE WHEN hr_tag = 'interview' THEN 1 ELSE 0 END) as interview_count,
                SUM(CASE WHEN hr_tag = 'pending' THEN 1 ELSE 0 END) as pending_count,
                SUM(CASE WHEN hr_tag = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
                SUM(CASE WHEN hr_tag IS NULL THEN 1 ELSE 0 END) as untagged_count
            FROM candidates
            WHERE position_id = ?
            """,(position_id,))

            row = cursor.fetchone()
            return {
                'total': row[0],
                'star':row[1],
                'interview':row[2],
                'pending':row[3],
                'rejected':row[4],
                'untagged':row[5],
            }
