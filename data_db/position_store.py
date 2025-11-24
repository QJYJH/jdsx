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
                             )

                """)
