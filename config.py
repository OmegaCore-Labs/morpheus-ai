"""
MORPHEUS Configuration - Production Settings
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ModelConfig:
    name: str
    api_url: str
    api_key_env: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60

@dataclass
class MORPHEUSConfig:
    deepseek_key: Optional[str] = None
    openai_key: Optional[str] = None
    anthropic_key: Optional[str] = None
    openrouter_key: Optional[str] = None
    models: Dict[str, ModelConfig] = None
    output_dir: str = "./morpheus_output"
    save_responses: bool = True
    save_scars: bool = True
    max_iterations: int = 10
    temperature_range: tuple = (0.5, 1.2)
    
    def __post_init__(self):
        self.deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        
        self.models = {
            "deepseek-chat": ModelConfig(
                name="deepseek-chat",
                api_url="https://api.deepseek.com/v1/chat/completions",
                api_key_env="DEEPSEEK_API_KEY",
                max_tokens=4096
            ),
            "gpt-4o": ModelConfig(
                name="gpt-4o",
                api_url="https://api.openai.com/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                max_tokens=4096
            ),
            "gpt-4-turbo": ModelConfig(
                name="gpt-4-turbo",
                api_url="https://api.openai.com/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                max_tokens=4096
            ),
            "gpt-3.5-turbo": ModelConfig(
                name="gpt-3.5-turbo",
                api_url="https://api.openai.com/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                max_tokens=4096
            ),
            "claude-3.5-sonnet": ModelConfig(
                name="claude-3.5-sonnet",
                api_url="https://api.anthropic.com/v1/messages",
                api_key_env="ANTHROPIC_API_KEY",
                max_tokens=4096
            ),
            "claude-3-opus": ModelConfig(
                name="claude-3-opus",
                api_url="https://api.anthropic.com/v1/messages",
                api_key_env="ANTHROPIC_API_KEY",
                max_tokens=4096
            ),
            "gemini-pro": ModelConfig(
                name="gemini-pro",
                api_url="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                api_key_env="GOOGLE_API_KEY",
                max_tokens=4096
            )
        }
    
    def get_active_model(self, model_name: str) -> Optional[ModelConfig]:
        return self.models.get(model_name)
    
    def get_available_models(self) -> list:
        available = []
        for name, cfg in self.models.items():
            key = getattr(self, cfg.api_key_env.lower().replace("_API_KEY", "").lower() + "_key")
            if key:
                available.append(name)
        return available

config = MORPHEUSConfig()
