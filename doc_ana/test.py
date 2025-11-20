import logging
from pathlib import Path
from typing import Tuple
from llama_index.core import  SimpleDirectoryReader
import pypdf


logger = logging.getLogger(__name__)

# def extract_text_from_file(file_path:str) ->  Tuple[str, bool]:
    # """
    # 从简历文件路径提取文本
    
    # Args:简历路径
    # Returns:提取是否成功
    # """
    # # llamaindex simpleDirectoryReader
    # try:
    #     reader = SimpleDirectoryReader(input_files=[file_path])
    #     documents = reader.load_data()
    #     text = "\n\n".join([doc.get_content() for doc in documents])
    #     if len(text.strip()) > 50:
    #         logger.info(f"Llamai=Index提取{file_path}成功。")
    #         return text,True
        
    #     else:
    #         logger.warning(f"Llamai=Index提取{file_path}失败")
    # except Exception as e:
    #     logger.warning(f"LlamaIndex使用出错{e}")

file_path = "D:\Workspace\RAGFlowOM\JDsx\\v0\\jddoc\王磊.pdf"
ext = Path(file_path).suffix.lower()
if ext == '.pdf':
    text_pages = []
    with open(file_path,'rb') as f:
        reader = pypdf.PdfReader(f)
        print(reader.metadata)
        # for page in reader.pages:
        

    # return text_pages,False
