from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseVectorDB(ABC):
    @abstractmethod
    async def create_collection(self, collection_name: str, vector_size: int):
        pass

    @abstractmethod
    async def upsert(self, collection_name: str, points: List[Dict[str, Any]]):
        pass

    @abstractmethod
    async def search(self, collection_name: str, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        pass
