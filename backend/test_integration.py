"""
测试综合方案生成API是否真实调用LLM
"""
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

from app.services.llm_client import get_llm_client, ChatMessage

async def test_integration():
    """测试两次调用是否返回不同内容"""

    client = get_llm_client()

    test_prompt = """基于以下智能体的分析结果，撰写"分析结论来源与整合方法说明"部分。

【各智能体分析结果】
### 国际法专家 (BLUE角色)
**法律立场**: 基于UNCLOS第56条，我国对EEZ享有主权权利。
**论据支撑**: 第77条明确沿海国对海床底土自然资源主权。
**策略建议**: 准备历史档案证据链。

【任务】
用80-100字说明：
1. 本报告整合了哪些角色的分析（我方律师/对手模拟/中立法官）
2. 整合方法：如何交叉验证和互补这些不同视角
3. 整合的价值：为何这种多视角分析更全面

【输出要求】
- 80-100字
- 客观陈述，体现专业性
- 不要输出标题，直接输出内容"""

    print("=== 第一次调用 ===")
    messages = [ChatMessage(role="user", content=test_prompt)]

    response1 = ""
    stream_gen = await client.chat(
        messages=messages,
        max_tokens=300,
        temperature=0.4,
        stream=True
    )
    async for chunk in stream_gen:
        if chunk:
            response1 += chunk
            print(chunk, end='', flush=True)

    print("\n\n=== 第二次调用（相同prompt）===")

    response2 = ""
    stream_gen = await client.chat(
        messages=messages,
        max_tokens=300,
        temperature=0.4,
        stream=True
    )
    async for chunk in stream_gen:
        if chunk:
            response2 += chunk
            print(chunk, end='', flush=True)

    print("\n\n=== 对比结果 ===")
    print(f"第一次长度: {len(response1)}字符")
    print(f"第二次长度: {len(response2)}字符")
    print(f"内容是否相同: {response1 == response2}")

    if response1 == response2:
        print("⚠️ 警告：两次调用返回完全相同的内容！")
        print("可能原因：温度太低、缓存、或Mock数据")
    else:
        print("✓ 确认：两次调用返回不同内容，LLM正常工作")

if __name__ == "__main__":
    asyncio.run(test_integration())
