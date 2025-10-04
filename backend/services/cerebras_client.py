"""Cerebras AI API client for Llama 3.1 8B model."""

import json
import httpx
from typing import Dict, List, Optional, Any
from config import settings


class CerebrasClient:
    """Client for interacting with Cerebras AI API."""
    
    def __init__(self):
        self.api_key = settings.cerebras_api_key
        self.base_url = settings.cerebras_api_base_url
        self.model_name = settings.model_name
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
        self.top_p = settings.top_p
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate a completion using Cerebras AI API with Llama 3.1 8B.
        
        Args:
            prompt: The user's input prompt
            system_message: Optional system message for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Dict containing the generated response and metadata
        """
        try:
            # Prepare messages
            messages = []
            
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "top_p": top_p or self.top_p,
                "stream": False
            }
            
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "model": result.get("model", self.model_name)
                }
                
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code} - {e.response.text}",
                "content": None
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
                "content": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "content": None
            }
    
    async def generate_with_context(
        self,
        user_question: str,
        context_documents: List[str],
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using RAG (Retrieval-Augmented Generation).
        
        Args:
            user_question: The user's question
            context_documents: Relevant documents retrieved from vector database
            system_message: Optional system message
            
        Returns:
            Dict containing the generated response
        """
        # Prepare context
        context = "\n\n".join(context_documents)
        
        # Create the prompt with context
        if system_message:
            prompt = f"{system_message}\n\nContext:\n{context}\n\nQuestion: {user_question}\n\nAnswer based on the provided context:"
        else:
            prompt = f"""You are a helpful AI assistant that answers questions based on the provided context. 
Use only the information from the context to answer the question. If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {user_question}

Answer:"""
        
        return await self.generate_completion(prompt, system_message)
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Cerebras AI API.
        
        Returns:
            Dict containing connection status
        """
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                
                response.raise_for_status()
                models = response.json()
                
                return {
                    "success": True,
                    "message": "Connection successful",
                    "available_models": [model.get("id") for model in models.get("data", [])]
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
