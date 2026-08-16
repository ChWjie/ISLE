import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from .base import BaseVectorDB

class QdrantVectorDB(BaseVectorDB):
    def __init__(self):
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", 6333))
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            # 简单的连通性测试
            self.client.get_collections()
            print(f"Connected to Qdrant at {self.host}:{self.port}")
            self.is_connected = True
        except Exception as e:
            print(f"Warning: Could not connect to Qdrant: {e}. Vector search will be disabled.")
            self.is_connected = False

    async def create_collection(self, collection_name: str, vector_size: int = 1536):
        if not self.is_connected: return False

        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )
            return True
        except Exception as e:
            # Collection可能已存在
            return False

    async def upsert(self, collection_name: str, points: List[Dict[str, Any]]):
        """
        points: list of dict with keys: id, vector, payload
        """
        if not self.is_connected: return False

        try:
            self.client.upsert(
                collection_name=collection_name,
                points=models.Batch(
                    ids=[p["id"] for p in points],
                    vectors=[p["vector"] for p in points],
                    payloads=[p["payload"] for p in points]
                )
            )
            return True
        except Exception as e:
            print(f"Upsert failed: {e}")
            return False

    async def search(self, collection_name: str, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        if not self.is_connected: return [] # 或者返回Mock数据

        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit
            )
            return [
                {"id": hit.id, "score": hit.score, "payload": hit.payload}
                for hit in search_result
            ]
        except Exception as e:
            print(f"Search failed: {e}")
            return []
