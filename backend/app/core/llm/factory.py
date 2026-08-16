from .base import BaseLLM
from .openai_adapter import OpenAILLM

class LLMFactory:
    @staticmethod
    def create(provider: str = "openai", **kwargs) -> BaseLLM:
        if provider == "openai":
            return OpenAILLM(**kwargs)
        # 预留 Ollama 等扩展
        return OpenAILLM(**kwargs)
