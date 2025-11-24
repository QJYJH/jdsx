"""岗位数据访问"""

import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from ..data_model.position import Position

class PositionStore:
    """数据库岗位数据管理"""

    def __init__(self,db_path:str = "./data_db/positions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()

    def _init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT DEFAULT 'active,'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
            """)
        
            # 创建触发器:自动更新updated_at
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS update_positions_timestamp
                AFTER UPDATE ON positions
                BEGIN 
                    UPDATE positions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)
    
    def create(self, position:Position) -> int:
        """创建岗位"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO positions (name, description,status),
                VALUES(?, ?, ?)
                """,
                (position.name, position.description,position.status)
            )
        return cursor.lastrowid
    
    def get_by_id(self, position_id:int) -> Optional[Position]:
        """根据id获取岗位信息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM positions WHERE id = ?",
                (position_id,)
            )
            row = cursor.fetchone()
            if row:
                return Position(**dict(row))
            return None
        
    def get_all(self,status:str = "active") -> List[Position]:
        """根据岗位状态获取所有岗位（默认active）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if status == "all":
                cursor = conn.execute(
                    "SELECT * FROM positions ORDER BY created_at DESC"
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM positions WHERE status = ? ORDER BY created_at QESC",
                    (status,)
                )
            rows = cursor.fetchall()
            return [Position(**dict(row)) for row in rows]
        
    def update(self,position_id:int, name:str = None,description:str = None,status: str = None) -> bool:
        """更新岗位信息"""
        updates = []
        params=[]

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if not updates:
            return False
        
        params.append(position_id)
        sql = f"UPDATE positions SET {', '.join(updates)} WHERE id =?"

        with  sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(sql, params)
            return cursor.rowcount > 0
        
    def delete(self,position_id:int ,soft_delete:bool = True) -> bool:
        """删除岗位"""
        with sqlite3.connect(self.db_path) as conn:
            if soft_delete:
                cursor = conn.execute(
                    "UPDATE positions SET status = 'delete' WHERE id = ?",
                    (position_id,)
                )
            else:
                cursor = conn.execute(
                    "DELETE FROM positions WHERE id = ?",
                    (position_id,)
                )
            return cursor.rowcount > 0
        
    # def count_candidates(self,positions_id:int) -> int:
    #     """统计岗位总候选人数量"""


