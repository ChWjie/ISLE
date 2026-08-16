from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        pass

    @abstractmethod
    async def generate_json(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]:
        pass
