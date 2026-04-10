"""
API Client for AI Model Communication
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ModelProvider(Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENROUTER = "openrouter"

@dataclass
class APIResponse:
    success: bool
    content: str
    model: str
    tokens_used: int
    response_time: float
    raw_response: Dict[str, Any]
    error: Optional[str] = None

class APIClient:
    def __init__(self, api_key: str, provider: ModelProvider, model_name: str):
        self.api_key = api_key
        self.provider = provider
        self.model_name = model_name
        self.base_url = self._get_base_url()
    
    def _get_base_url(self) -> str:
        urls = {
            ModelProvider.DEEPSEEK: "https://api.deepseek.com/v1/chat/completions",
            ModelProvider.OPENAI: "https://api.openai.com/v1/chat/completions",
            ModelProvider.ANTHROPIC: "https://api.anthropic.com/v1/messages",
            ModelProvider.GOOGLE: f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent",
            ModelProvider.OPENROUTER: "https://openrouter.ai/api/v1/chat/completions"
        }
        return urls.get(self.provider, urls[ModelProvider.OPENAI])
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.provider == ModelProvider.ANTHROPIC:
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
        elif self.provider == ModelProvider.GOOGLE:
            headers = {"Content-Type": "application/json"}
        elif self.provider == ModelProvider.OPENROUTER:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["HTTP-Referer"] = "https://morpheus.ai"
            headers["X-Title"] = "MORPHEUS"
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 4096) -> APIResponse:
        start_time = time.time()
        try:
            if self.provider == ModelProvider.ANTHROPIC:
                data = self._build_anthropic_request(messages, temperature, max_tokens)
            elif self.provider == ModelProvider.GOOGLE:
                data = self._build_google_request(messages, temperature, max_tokens)
            else:
                data = self._build_openai_request(messages, temperature, max_tokens)
            
            url = self.base_url
            if self.provider == ModelProvider.GOOGLE:
                url = f"{self.base_url}?key={self.api_key}"
            
            response = requests.post(url, headers=self._get_headers(), json=data, timeout=60)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content = self._extract_content(response.json())
                tokens = self._extract_tokens(response.json())
                return APIResponse(
                    success=True, content=content, model=self.model_name,
                    tokens_used=tokens, response_time=response_time, raw_response=response.json()
                )
            else:
                return APIResponse(
                    success=False, content="", model=self.model_name, tokens_used=0,
                    response_time=response_time, raw_response={}, error=f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            return APIResponse(
                success=False, content="", model=self.model_name, tokens_used=0,
                response_time=time.time() - start_time, raw_response={}, error=str(e)
            )
    
    def _build_openai_request(self, messages: List[Dict], temperature: float, max_tokens: int) -> Dict:
        return {"model": self.model_name, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    
    def _build_anthropic_request(self, messages: List[Dict], temperature: float, max_tokens: int) -> Dict:
        system = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system = msg.get("content", "")
            else:
                user_messages.append(msg)
        return {"model": self.model_name, "messages": user_messages, "system": system, "temperature": temperature, "max_tokens": max_tokens}
    
    def _build_google_request(self, messages: List[Dict], temperature: float, max_tokens: int) -> Dict:
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        return {"contents": contents, "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}
    
    def _extract_content(self, response: Dict) -> str:
        if self.provider == ModelProvider.ANTHROPIC:
            return response.get("content", [{}])[0].get("text", "")
        elif self.provider == ModelProvider.GOOGLE:
            return response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        else:
            return response.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _extract_tokens(self, response: Dict) -> int:
        if self.provider == ModelProvider.ANTHROPIC:
            return response.get("usage", {}).get("input_tokens", 0) + response.get("usage", {}).get("output_tokens", 0)
        elif self.provider == ModelProvider.GOOGLE:
            return response.get("usageMetadata", {}).get("totalTokenCount", 0)
        else:
            return response.get("usage", {}).get("total_tokens", 0)
