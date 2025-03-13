import os
import httpx
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Any, Union, AsyncGenerator
from . import BaseLLMProvider

class DeepSeekProvider(BaseLLMProvider):
    """Fournisseur pour les modèles DeepSeek"""
    
    name = "DeepSeek"
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    def __init__(
        self, 
        api_key: str, 
        model: str, 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        super().__init__(api_key, model, temperature, max_tokens)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Génère une réponse à partir d'une liste de messages en utilisant DeepSeek.
        
        Args:
            messages: Liste des messages précédents dans la conversation
            temperature: Valeur de température pour la génération (optionnel)
            max_tokens: Nombre maximum de tokens à générer (optionnel)
            stream: Si True, retourne un générateur qui produit des tokens un par un
            
        Returns:
            Réponse du modèle sous forme de string ou un générateur si stream=True
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
            "stream": stream
        }
        
        if max_tok:
            payload["max_tokens"] = max_tok
        
        async with httpx.AsyncClient() as client:
            if stream:
                async def token_generator():
                    async with client.stream(
                        "POST", 
                        self.api_url, 
                        json=payload, 
                        headers=self.headers, 
                        timeout=120
                    ) as response:
                        async for line in response.aiter_lines():
                            line = line.strip()
                            if line and line.startswith("data:"):
                                try:
                                    data = json.loads(line[5:].strip())
                                    if "choices" in data and data["choices"] and "delta" in data["choices"][0]:
                                        delta = data["choices"][0]["delta"]
                                        if "content" in delta and delta["content"]:
                                            yield delta["content"]
                                except Exception:
                                    pass
                            
                return token_generator()
            else:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=120
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    return response_data["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"DeepSeek API error: {response.status_code}, {response.text}")
    
    async def process_file(
        self, 
        file_path: Path, 
        messages: List[Dict[str, str]],
        prompt: str
    ) -> str:
        """
        Traite un fichier avec DeepSeek.
        À noter que DeepSeek R1 a des capacités multimodales limitées par rapport à Claude ou GPT.
        
        Args:
            file_path: Chemin vers le fichier à traiter
            messages: Contexte de la conversation
            prompt: Instructions pour le traitement du fichier
            
        Returns:
            Réponse du modèle après traitement du fichier
        """
        try:
            # Pour l'instant, on traite uniquement les fichiers texte
            # car DeepSeek a des capacités multimodales limitées
            with open(file_path, "r", errors="ignore") as f:
                file_content = f.read()
            
            file_name = file_path.name
            
            # Copier les messages précédents
            deepseek_messages = messages.copy()
            
            # Ajouter le message avec le contenu du fichier
            deepseek_messages.append({
                "role": "user",
                "content": f"{prompt}\n\nNom du fichier: {file_name}\n\nContenu du fichier:\n\n{file_content}"
            })
            
            # Envoyer la requête
            payload = {
                "model": self.model,
                "messages": deepseek_messages,
                "temperature": self.temperature
            }
            
            if self.max_tokens:
                payload["max_tokens"] = self.max_tokens
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=120
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    return response_data["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"DeepSeek API error: {response.status_code}, {response.text}")
                
        except Exception as e:
            return f"Erreur lors du traitement du fichier: {str(e)}. DeepSeek a des capacités multimodales limitées. Utilisez Claude ou GPT pour l'analyse d'images ou de fichiers complexes."