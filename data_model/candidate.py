"""候选人模型"""
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class WorkExperience(BaseModel):
    """工作经历"""
    company: str  = Field(description="公司名称")
    position: str = Field(description="职位")
    start_time: Optional[str] = Field(description="入职日期",default=None)
    end_time: Optional[str] = Field(description="离职时间",default=None)
    description: str = Field(description="详细描述在职期间的工作职责和成就")
    
    

