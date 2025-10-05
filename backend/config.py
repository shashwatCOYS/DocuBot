"""Configuration settings for the DocuBot backend."""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


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
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed_origins string into a list."""
        if not self.allowed_origins:
            return []
        return [origin.strip() for origin in self.allowed_origins.split(',') if origin.strip()]
    
    # MCP Server configuration
    exa_mcp_base_url: str | None = None  # e.g., http://localhost:7777
    exa_api_key: str | None = None
    exa_search_tool_name: str = "exa.search"  # tool id as exposed by MCP server
    exa_crawl_tool_name: str = "exa.crawl"    # if crawl tool is distinct
    use_mcp_for_crawling: bool = False
    
    # Context7 configuration
    context7_api_key: str | None = None
    
    # Vector Database configuration
    weaviate_url: str = "http://localhost:8080"
    use_cloud_vectordb: bool = True
    
    # Pinecone configuration
    pinecone_api_key: str | None = None
    pinecone_environment: str | None = None
    pinecone_index_name: str = "docubot-index"
    use_pinecone: bool = False
    pinecone_mcp_base_url: str | None = None  # e.g., http://localhost:7779
    
    # Redis configuration
    redis_url: str = "redis://localhost:6379"
    
    # Caching disabled
    enable_caching: bool = False
    
    # Web crawling configuration
    max_crawl_depth: int = 20  # Deep crawling for comprehensive coverage
    max_concurrent_requests: int = 15  # Increased for faster crawling
    crawl_delay: float = 0.3  # Reduced delay for faster crawling
    max_pages_per_domain: int = 5000  # Maximum pages to crawl per domain
    same_domain_only: bool = True  # Only crawl pages within the same domain
    respect_robots_txt: bool = False  # Ignore robots.txt for comprehensive crawling
    follow_redirects: bool = True  # Follow redirects for complete coverage
    extract_images: bool = True  # Extract image alt text and captions
    extract_tables: bool = True  # Extract table content
    extract_code_blocks: bool = True  # Extract code blocks and examples
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
