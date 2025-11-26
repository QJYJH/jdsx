import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from collections import defaultdict

# LlamaIndex imports
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
    Document
)
from llama_index.core.node_parser import NodeParser
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator

from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.xinference import XinferenceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

import chromadb

from .data_db.candidate_store import CandidateStore

logger = logging.getLogger(__name__)


class MultiPositionNodeParser(NodeParser):
     """
    多岗位的简历Node解析器;
        每份简历作为一个完整的node，不进行分块;
        在metadata中添加position_id用于多岗位隔离
        添加candidate_name用于候选人识别
    """
     def _parse_nodes(self, documents:List[Document], **kwargs: Any) -> List[BaseNode]:
        """
        将每份简历作为一个完整的node进行向量化
        Args:
            documents: 文档列表（可能包含多页PDF）
            **kwargs: 必须包含position_id

        Returns:
            包含完整简历的node列表（每份简历1个node）
        """
        all_nodes = []

        # 从kwargs中获取position_id
        position_id = kwargs.get("position_id")
        # 按文件路径分组（一个文件可能有多页）
        docs_by_filepath = defaultdict(list)  # 自动创建键值
        for doc in documents:
            docs_by_filepath[doc.metadata.get("file_path")].append(doc)
        
        for file_path ,doc_parts in docs_by_filepath.items():
            doc_parts.sort(key=lambda d:int (d.metadata.get("page_label","0")))
            full_text = "\n\n".join([d.get_content().strip() for d in doc_parts])
            
            # 跳过空文档
            if not full_text.strip():
                continue

            metadata = doc_parts[0].metadata.copy()
            metadata["position_id"] = position_id
            metadata["candidate_name"] = Path(file_path).stem # 提取无后缀的文件名
            metadata["chunk_type"] = "full_resume"
            metadata["resume_length"] = len(full_text)

            node = TextNode(text = full_text, metadata = metadata)
            all_nodes.append(node)
            logger.info(f"创建完整简历node: {metadata['candidate_name']} (长度: {len(full_text)} 字符)")

        return all_nodes


class RAGEngine:
    def _init__(self, config:Dict[str,Any]) -> None:
        self.config = config
        self.documents_path = Path("./jddoc")
        self._LlamaIndex_embedding()
        # 加载或创建向量索引
        self._load_or_create_index()

        # 候选人存储
        self.candidate_store = CandidateStore()

        logger.info("RAGEngine V2 initialized successfully.")

    def _LlamaIndex_embedding(self):
         """配置LlamaIndex的全局LLM和嵌入模型"""
         Settings.llm = OpenAILike(
              model = self.config["vllm"]["vllm_model"],
              api_base= self.config["vllm"]["vllm_api"],
              api_key= self.config["vllm"]["vllm_key"]

         )
         Settings.embed_model = XinferenceEmbedding(
              model_uid=self.config["embedding"]["em_model"],
              base_url=self.config["embedding"]["base_url"]
         )
        
    def _load_or_create_index(self):
        """加载或创建向量索引"""
        try:
            db = chromadb.PersistentClient(
                path = Path("./vector_db"),
                tenant="default_tenant",
                database="default_database"

            )
        except Exception as e:
            logger.warning(f"New ChromaDB API failed, trying legacy mode: {e}")
            db = chromadb.PersistentClient(path="./vector_db")
        
        chromadb_collection = db.get_or_create_collection(self.config["model"]["collection_name"])
        vector_store = ChromaVectorStore(chroma_collection=chromadb_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context = storage_context
        )
        logger.info("vectorStoreIndex load success")
    
    def ingest_resume(
        self,
        file_path:str,
        position_id:int,
        candidate_name:str = None
    ) -> bool:
        """
        摄取单个简历到向量数据库

        Args:
            file_path: 简历文件路径
            position_id: 岗位ID
            candidate_name: 候选人姓名(可选,默认从文件名提取)

        Returns:
            是否成功
        """
        try:
            reader = SimpleDirectoryReader(input_files=[file_path])
            documents = reader.load_data()

            parser = MultiPositionNodeParser()
            nodes = parser.get_nodes_from_documents(documents=documents, position_id = position_id)
            
            if not nodes:
                logger.warning(f"未提取到有效节点")
                return False
            pipeline = IngestionPipeline(transformations=[Settings.embed_model])
            nodes_with_embeddings = pipeline.run(nodes=nodes)
            self.index.insert_nodes(nodes_with_embeddings)

            logger.info("成功插入节点到向量索引")
            return True
        
        except Exception as e:
            logger.error("简历提取失败")
            return False
        
    def retrieve(
        self,
        query:str,
        position_id: int = None,
        top_k: int = 5
    ) -> List[Any]:
        """
        检索相关文档节点

        Args:
            query: 查询文本
            position_id: 岗位ID(如果指定,则只检索该岗位的简历)
            top_k: 返回结果数量

        Returns:
            检索到的节点列表
        """
        logger.info(f"检索查询: '{query[:100]}...', 岗位ID: {position_id}, top_k: {top_k}")

        # metadata过滤器
        filters = None
        if position_id is not None:
            filters = MetadataFilters(
                filters = [MetadataFilter(
                    key="position_id",
                    value=position_id,
                    operator=FilterOperator.EQ
                )]
            )
        
        # 检索器
        retriever = self.index.as_retriever(
            similarity_top_k = top_k,
            filters = filters
        )
        
        # 执行检索
        retrieved_nodes = retriever.retrieve(query)
        logger.info(f"检索到{len(retrieved_nodes)}个节点")
        
        return retrieved_nodes
    
    def clear_position_data(self, position_id: int):
        """清空指定岗位的向量数据"""
        # ChromaDB不直接支持按metadata删除,这里需要重建索引
        # 实际场景中可以考虑其他方案
        logger.warning("向量库不支持按metadata删除,建议重建整个索引")
        pass
