def get_config():
    """
    提供应用程序的配置。
    """
    return {
        "model": {
            "llm_model": "deepseek-chat",  # 模型名称
            "deepseek_key": "sk-4219d44e4ec24f9b8c678fdc549074fc",
            "ollama_embedding_model": "bge-m3", # 嵌入模型名称
            "collection_name": "resume_collection" # ChromaDB collection 名称
        },
        "embedding":{
            "em_model":"bge-m3",
            "base_url":"http://192.168.2.120:9997",

        },
        "vllm":{
            "vllm_model":"Qwen3-32B",
            "vllm_api":"http://192.168.2.120:8207/v1",
            "vllm_key":"dI.=>.TU?E5l>Ac8,Zz4"
        },
        "env": {
            "ollama_host": "https://api.deepseek.com",  # Ollama服务地址
            "ollama_timeout": 120.0  # Ollama请求超时时间（秒）
        }
    }
