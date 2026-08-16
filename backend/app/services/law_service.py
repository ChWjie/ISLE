from typing import List, Dict, Any
from app.core.vector_db.qdrant import QdrantVectorDB
from app.core.llm.factory import LLMFactory

class LawService:
    def __init__(self):
        self.vector_db = QdrantVectorDB()
        self.llm = LLMFactory.create()
        self.collection_name = "law_docs"

    async def initialize(self):
        await self.vector_db.create_collection(self.collection_name)

    async def search_relevant_laws(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # 1. TODO: Generate embedding for query (Need Embedding Model)
        # mock embedding for now if no real model is available from OpenAI
        query_vector = [0.1] * 1536

        results = await self.vector_db.search(self.collection_name, query_vector, limit)
        return results

    async def analyze_legal_issues(self, question: str, context_docs: List[Dict]) -> str:
        context_str = "\n".join([f"- {doc['payload']['title']}: {doc['payload']['content']}" for doc in context_docs])

        prompt = f"""
        基于以下法律上下文回答问题：
        {context_str}

        问题: {question}
        """

        system_prompt = "你是一个法律专家助手，请基于提供的法律条文进行严谨的分析。"

        return await self.llm.generate(prompt, system_prompt=system_prompt)
