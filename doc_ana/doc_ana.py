import logging
from pathlib import Path
from typing import Tuple
from llama_index.core import  SimpleDirectoryReader
import pypdf
import docx2txt


logger = logging.getLogger(__name__)

def extract_text_from_file(file_path:str) ->  Tuple[str, bool]:
    """
    从简历文件路径提取文本
    
    Args:简历路径
    Returns:提取是否成功
    """
    # llamaindex simpleDirectoryReader
    try:
        reader = SimpleDirectoryReader(input_files=[file_path])
        documents = reader.load_data()
        
        text = "\n\n".join([doc.get_content() for doc in documents])
        if len(text.strip()) > 50: # strip() 方法用于移除字符串开头和结尾的指定字符（默认为空格或换行符）。
            logger.info(f"LlamaIndex提取{file_path}成功。")
            return text,True
        
        else:
            logger.warning(f"LlamaIndex提取{file_path}失败")
    except Exception as e:
        logger.warning(f"LlamaIndex使用出错{e}")
    
    ext = Path(file_path).suffix.lower()
    if ext == '.pdf':
        try:
            text_pages = []
            with open(file_path,'rb') as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_pages.append(page_text)
            text = "\n\n".join(text_pages)

            if len(text.strip()) > 50:
                logger.info(f"pypdf提取成功{file_path}")
                return text, True
        
        except Exception as e:
            logger.warning(f"pypdf提取失败{file_path}")
    
    elif ext == '.docx':
        try:
            text = docx2txt.process(file_path)
            if len(text.strip()) > 50:
                logger.info(f"docx2txt提取成功{file_path}")
                return text, True

        except Exception as e:
            logger.warning(f"docx2txt提取失败{e}")
    
    elif ext == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            if len(text.strip()) > 50:
                logger.info(f"TXT提取成功{file_path}")
                return text, True

        except Exception as e:
            logger.warning(f"TXT提取失败{e}")


    # ===== 策略 3: 完全失败 =====
    logger.error(f"提取失败: {file_path}")
    return "", False

# 验证简历内容
def validate_resume_content(text: str) -> bool:
    """
    验证提取的文本是否为有效简历,1. 长度 >= 50 字符;2. 包含简历常见关键词

    Args:简历内容
    Return:bool
    """

    # 规则 1: 长度检查
    if len(text.strip()) < 50:
        logger.warning(f"⚠️ 文本过短: {len(text)} 字符")
        return False

    # 规则 2: 关键词检查
    resume_keywords = [
        "教育", "学历", "工作", "经验", "技能", "项目",
        "姓名", "联系", "电话", "邮箱", "职责", "任职",
        "大学", "本科", "硕士", "博士", "公司", "负责"
    ]

    keyword_count = sum(1 for kw in resume_keywords if kw in text)

    if keyword_count < 2:
        logger.warning(f"⚠️ 关键词匹配不足: 仅匹配 {keyword_count} 个")
        return False

    logger.info(f"✅ 简历内容验证通过 (长度: {len(text)}, 关键词: {keyword_count})")
    return True


res = extract_text_from_file("D:\Workspace\RAGFlowOM\JDsx\\v0\\jddoc\李静.docx")
print(res)