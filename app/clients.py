import os
import json
import requests
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel
from openai import OpenAI
import google.generativeai as genai

class PerplexityClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro"

    def search(self, query: str, system_prompt: str = "You are a helpful research assistant.") -> Dict[str, Any]:
        """
        Performs a search using Perplexity API.
        Returns a dictionary with 'content' and 'citations'.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            citations = data.get("citations", [])

            return {
                "content": content,
                "citations": citations
            }
        except Exception as e:
            raise Exception(f"Error calling Perplexity API: {e}")

class LLMClient:
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key

        if self.provider == "openai":
            self.api_key = self.api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4o"

        elif self.provider == "gemini":
            self.api_key = self.api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            genai.configure(api_key=self.api_key)
            self.model = "gemini-1.5-pro-latest"

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def extract_data(self, content: str, schema: Type[BaseModel], system_instructions: str = "") -> BaseModel:
        """
        Extracts structured data from the content using the specified schema.
        """
        prompt = f"{system_instructions}\n\nPlease extract the following information from the text provided below:\n\n{content}"

        if self.provider == "openai":
            try:
                completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a precise data extraction expert."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format=schema
                )
                return completion.choices[0].message.parsed
            except Exception as e:
                raise Exception(f"Error calling OpenAI: {e}")

        elif self.provider == "gemini":
            try:
                model = genai.GenerativeModel(self.model)
                result = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=schema
                    )
                )
                return schema.model_validate_json(result.text)
            except Exception as e:
                raise Exception(f"Error calling Gemini: {e}")

        return schema()
