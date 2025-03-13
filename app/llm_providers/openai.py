import os
import base64
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Any, Union, AsyncGenerator
from openai import AsyncOpenAI
from . import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    """Fournisseur pour les modèles GPT d'OpenAI"""
    
    name = "OpenAI GPT"
    
    def __init__(
        self, 
        api_key: str, 
        model: str, 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Génère une réponse à partir d'une liste de messages en utilisant GPT.
        
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
        
        if stream:
            response_stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                stream=True
            )
            
            async def token_generator():
                async for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            return token_generator()
        else:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                stream=False
            )
            return response.choices[0].message.content
    
    async def process_file(
        self, 
        file_path: Path, 
        messages: List[Dict[str, str]],
        prompt: str
    ) -> str:
        """
        Traite un fichier avec GPT Vision.
        
        Args:
            file_path: Chemin vers le fichier à traiter
            messages: Contexte de la conversation
            prompt: Instructions pour le traitement du fichier
            
        Returns:
            Réponse du modèle après traitement du fichier
        """
        # Déterminer le type MIME du fichier
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # Vérifier si c'est une image
        is_image = mime_type.startswith("image/")
        
        if is_image:
            # Lire le contenu du fichier
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            # Encoder le fichier en base64
            file_b64 = base64.b64encode(file_content).decode("utf-8")
            
            # Préparer le message avec l'image
            file_message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{file_b64}"}}
                ]
            }
            
            # Copier les messages précédents et ajouter le message avec l'image
            openai_messages = messages.copy()
            openai_messages.append(file_message)
            
            # Utiliser le modèle avec vision
            vision_model = "gpt-4-vision-preview" if "gpt-4" in self.model else self.model
            
            response = await self.client.chat.completions.create(
                model=vision_model,
                messages=openai_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens or 4096
            )
            
            return response.choices[0].message.content
        else:
            # Pour les fichiers non-image, on les traite comme des textes
            # Cela fonctionnera pour les fichiers texte, mais pas pour les binaires
            with open(file_path, "r", errors="ignore") as f:
                file_content = f.read()
            
            file_message = {
                "role": "user",
                "content": f"{prompt}\n\nContenu du fichier:\n\n{file_content}"
            }
            
            openai_messages = messages.copy()
            openai_messages.append(file_message)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens or 4096
            )
            
            return response.choices[0].message.content