import streamlit as st
import re
import requests
import uuid  # 👈 新增导入
from pathlib import Path

# --- 核心应用逻辑 ---
# from rag_engine import RAGEngine
# from application import ResumeApplication
from config import get_config

# def get_chat_model(config:dict) -> list[str]:
#     return 

def ini_st_state():
    st.session_state.rag = get_config()
    return st.session_state.rag



res = ini_st_state()
print(res)