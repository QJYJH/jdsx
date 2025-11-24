"""岗位模型"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Position(BaseModel):
    id:Optional[int] = None
    name: str = Field(description="岗位的名称")
    description: str = Field(description="详细、完整的岗位描述")
    status: str = Field(default="active", description="该岗位的状态:active/inactive/deleted")
    created_at: Optional[datetime] = None
    updated_at:Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime:lambda v:v.isoformat() if v else None
        }
