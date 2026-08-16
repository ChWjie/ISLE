"""
测试LLM配置和API调用
"""
import asyncio
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

from app.services.llm_client import get_llm_client, ChatMessage

async def test_llm():
    client = get_llm_client()

    print("=== LLM配置信息 ===")
    print(f"API Key configured: {bool(client.config.api_key)}")
    print(f"Base URL: {client.config.base_url}")
    print(f"Model: {client.config.model}")
    print(f"Temperature: {client.config.temperature}")
    print(f"Max Tokens: {client.config.max_tokens}")

    print("\n=== 测试Stream调用 ===")
    try:
        messages = [ChatMessage(role="user", content="请用20字描述联合国海洋法公约")]

        stream_gen = await client.chat(
            messages=messages,
            max_tokens=50,
            temperature=0.3,
            stream=True
        )

        full_response = ""
        async for chunk in stream_gen:
            if chunk:
                print(chunk, end='', flush=True)
                full_response += chunk

        print(f"\n\n✓ Stream调用成功！")
        print(f"响应长度: {len(full_response)}字符")

    except Exception as e:
        print(f"\n✗ Stream调用失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm())
