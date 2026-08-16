import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from .base import BaseLLM

from app.config import get_settings

class OpenAILLM(BaseLLM):
    def __init__(self, api_key: str = None, model: str = None):
        settings = get_settings()
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model = model or settings.OPENAI_MODEL
        self.client = None
        if self.api_key:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=60.0,
                max_retries=2
            )
        else:
            print("Warning: OPENAI_API_KEY not found. LLM calls will fail.")

    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        if not self.client:
             return "Error: OpenAI API Key not configured."

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return f"Error calling OpenAI: {str(e)}"

    async def generate_json(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]:
        if not self.client:
             return {"error": "OpenAI API Key not configured."}

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt + "\nResponse must be valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                **kwargs
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"LLM JSON Error: {e}")
            return {"error": f"Error calling OpenAI: {str(e)}"}
