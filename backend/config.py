"""Configuration settings for the DocuBot backend."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Cerebras AI API Configuration
    cerebras_api_key: str = "your_cerebras_api_key_here"
    cerebras_api_base_url: str = "https://api.cerebras.ai/v1"
    
    # Model Configuration
    model_name: str = "llama-3.1-8b"
    max_tokens: int = 2048
    temperature: float = 0.5
    top_p: float = 0.9
    
    # Database Configuration
    chroma_persist_directory: str = "./chroma_db"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
