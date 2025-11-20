"""AI分析结果模型"""
from typing_extensions import Self
from pydantic import BaseModel,Field,field_validator
from typing import Any, List,Dict,Optional


class WorkExperienceExtracted(BaseModel):
    """
    提取工作经验模型
    """
    company:str
    position:str
    start_time:Optional[str] = None
    end_time:Optional[str] = None
    description:str = Field(default="")

class ProjectExperienceExtracted(BaseModel):
    pro_name:str
    role:str
    description:str = Field(default="")


class ResumeAnalysis(BaseModel):
    recommendation_level:str = Field(
        default="可考虑",
        description="推荐等级：强烈推荐 | 推荐 | 可考虑 | 不推荐"
    )


    key_strengths:List[str] = Field(
        default_factory=list,
        description="具体、可验证的优势，先列出与岗位相关的亮点"
    )
    
    key_concerns: List[str] = Field(
        default_factory=list,
        description="需要关注的方面，客观指出不要夸大"
    )

    one_sentence_summary: str = Field(
        default="",
        description="用一段话概括简历内容的核心特征，帮助HR快速简历印象"
    )

    total_year_experience:int = Field(
        default=0,
        description="工作总年数"
    )

    work_experience: List[WorkExperienceExtracted] = Field(
        default_factory=list,
        description="工作经历列表"
    )

    project_experience: List[ProjectExperienceExtracted] = Field(
        default_factory=list,
        description="项目经验列表"
    )

    analysis_success: bool = Field(default=True, description="AI是否分析完成")
    @field_validator('key_strengths', 'key_concerns')
    @classmethod
    def remove_empty_items(cls,v):
        """移除空字符串"""
        if isinstance(v, list):
            return [item.strip() for item in v if item and item.strip()]
        return v
    
    @field_validator('recommendation_level')
    @classmethod
    def validate_level(cls,v):
        """校验简历推荐等级"""
        valid_levels = ["强烈推荐","推荐","可考虑","不推荐"]
        if v not in valid_levels:
            return "可考虑"
        return v
    
    @field_validator('key_strengths')
    @classmethod
    def validate_strengths_counts(cls,v):
        """记录优势有多少条"""
        if not v or len(v) <= 1:
            return["优势较少，请查看简历原文进行人工评估"]
        return v
    
    @field_validator('key_concerns')
    @classmethod
    def validate_concerns_counts(cls, v):
        """限制3个点"""
        if v and len(v) >3:
            return v[:3]
        return v

