"""
LLM Service Abstraction Layer
支持多种API Provider，统一调用接口
"""
import os
from typing import List, Dict, Optional, AsyncGenerator
import httpx
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str  # system, user, assistant
    content: str


class LLMConfig(BaseModel):
    """LLM配置"""
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    temperature: float = 0.3
    max_tokens: int = 200


class LLMClient:
    """
    LLM客户端抽象层
    支持OpenAI兼容接口 (DeepSeek, OpenAI, Azure等)
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """
        聊天补全接口

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出

        Returns:
            完整响应文本 或 流式生成器
        """
        payload = {
            "model": self.config.model,
            "messages": [msg.dict() for msg in messages],
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": stream
        }

        if stream:
            return self._stream_chat(payload)
        else:
            return await self._sync_chat(payload)

    async def _sync_chat(self, payload: dict) -> str:
        """同步聊天"""
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _stream_chat(self, payload: dict) -> AsyncGenerator[str, None]:
        """流式聊天"""
        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]  # 去掉 "data: " 前缀
                    if chunk == "[DONE]":
                        break
                    try:
                        import json
                        data = json.loads(chunk)
                        delta = data["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]
                    except:
                        continue

    async def embed(self, text: str) -> List[float]:
        """
        文本向量化 (用于RAG)

        Args:
            text: 输入文本

        Returns:
            向量列表
        """
        payload = {
            "model": "text-embedding-ada-002",  # 可配置
            "input": text
        }
        response = await self.client.post("/embeddings", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局LLM客户端实例
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取全局LLM客户端"""
    global _llm_client
    if _llm_client is None:
        config = LLMConfig(
            api_key=os.getenv("LLM_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
            model=os.getenv("LLM_MODEL", "deepseek-chat"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "200"))
        )
        _llm_client = LLMClient(config)
    return _llm_client


async def init_llm_client():
    """初始化LLM客户端 (在app启动时调用)"""
    global _llm_client
    _llm_client = get_llm_client()
    print(f"✓ LLM Client initialized: {_llm_client.config.model}")


async def close_llm_client():
    """关闭LLM客户端 (在app关闭时调用)"""
    global _llm_client
    if _llm_client:
        await _llm_client.close()
        print("✓ LLM Client closed")
