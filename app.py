import streamlit as st
import re
import requests
import uuid  # 👈 新增导入
from pathlib import Path

# --- 储存 ---
from .data_db.position_store import PositionStore
from .data_db.candidate_store import CandidateStore
from .data_db.candinote_store import  NoteStore
from rag_engine import RAGEngine

# --- 服务 ---
from config import get_config

# --- llamaindex ---
from llama_index.core import Settings

# --- ui ---
def get_chat_model(config:dict) -> list[str]:
    return [config['vllm']['vllm_model']]

def ini_app():
    """初始化应用"""
    
    if 'app_ini' not in st.session_state:
        with st.spinner("正在初始化系统..."):
            # 获取配置
            config = get_config()
            # 初始化存储
            st.session_state.position_store = PositionStore()
            st.session_state.candidate_store = CandidateStore()
            st.session_state.note_store = NoteStore()
            st.session_state.rag_engine = RAGEngine()

            # 服务

def render_sidebar():
    """侧边栏渲染"""
    with st.sidebar:
        st.divider()
        



    return 

def main():
    """主函数"""

    # 页面设置
    st.set_page_config(
        page_title='简历筛选系统',
        layout='wide'
    )

config = get_config()
res = get_chat_model(config)
print(res)