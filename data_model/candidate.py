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
    
    
class ProjectExperience(BaseModel):
    """项目经历"""
    name: str = Field(description="项目名称")
    role: str = Field(description="在项目中的角色")
    description: str = Field(description="项目的详细描述，使用的技术和取得的成果")

class Skills(BaseModel):
    """技能"""
    category: str = Field(description="技能类别（例如：AI与数据技术，产品管理，编程语言）")
    items: List[str] = Field(description="该类别下的具体技能列表")

class CandidateProfile(BaseModel):
    """候选人完整档案"""
    # 基础信息
    id: Optional[int] = None
    name: str = Field(description="候选人姓名")
    position_id: int = Field(description="关联的岗位id")
    file_name: str = Field(description="原始简历文件名",default="")

    # 原有的档案字段
    total_years_experience:int = Field(description="总工作年限（数字）",default=0)
    work_experience: List[WorkExperience] = Field(description="工作经验列表",default_factory=list)
    project_experience: List[ProjectExperience] = Field(description="项目经历列表",default_factory=list)
    skills: List[Skills] = Field(description="技能列表",default_factory=list)

    # 2、AI分析
    recommendation_level: str = Field(default="可考虑",description="推荐等级")
    ai_strengths:List[str] = Field(default_factory=list,description="AI分析的申请人关键优势")
    ai_concerns:List[str] = Field(default_factory=list,description="AI分析的需关注点")
    ai_summary:str = Field(default="",description="AI一句话总结")

    #3、HR标签
    hr_tag:Optional[str] = None
    hr_note:Optional[str] = None
    hr_tagged_at:Optional[datetime] = None

    # 解析状态
    parser_status: str = Field(default="success",description="文档解析状态：success/failed")
    error_message:Optional[str] = None

    #时间戳
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isotime()if v else None
        }



