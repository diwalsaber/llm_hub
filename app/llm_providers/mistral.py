import os
from pathlib import Path
from typing import List, Dict, Optional, Any, Union, AsyncGenerator
import mistralai.async_client as mistral
from mistralai.models.chat_completion import ChatMessage
from . import BaseLLMProvider

class MistralProvider(BaseLLMProvider):
    """Fournisseur pour les modèles Mistral AI"""
    
    name = "Mistral AI"
    
    def __init__(
        self, 
        api_key: str, 
        model: str, 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = mistral.MistralAsyncClient(api_key=api_key)
    
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Génère une réponse à partir d'une liste de messages en utilisant Mistral.
        
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
        
        # Convertir les messages au format Mistral
        mistral_messages = []
        for msg in messages:
            role = msg["role"]
            if role == "system":
                mistral_messages.append(ChatMessage(role="system", content=msg["content"]))
            elif role == "user":
                mistral_messages.append(ChatMessage(role="user", content=msg["content"]))
            elif role == "assistant":
                mistral_messages.append(ChatMessage(role="assistant", content=msg["content"]))
        
        if stream:
            response_stream = await self.client.chat_stream(
                model=self.model,
                messages=mistral_messages,
                temperature=temp,
                max_tokens=max_tok
            )
            
            async def token_generator():
                async for chunk in response_stream:
                    if chunk.delta:
                        yield chunk.delta
            
            return token_generator()
        else:
            response = await self.client.chat(
                model=self.model,
                messages=mistral_messages,
                temperature=temp,
                max_tokens=max_tok
            )
            return response.choices[0].message.content
    
    async def process_file(
        self, 
        file_path: Path, 
        messages: List[Dict[str, str]],
        prompt: str
    ) -> str:
        """
        Traite un fichier avec Mistral.
        Remarque: Mistral ne supporte pas nativement l'analyse d'images comme Claude ou GPT,
        nous allons donc traiter le fichier comme du texte.
        
        Args:
            file_path: Chemin vers le fichier à traiter
            messages: Contexte de la conversation
            prompt: Instructions pour le traitement du fichier
            
        Returns:
            Réponse du modèle après traitement du fichier
        """
        try:
            # Essayer de lire le fichier comme du texte
            with open(file_path, "r", errors="ignore") as f:
                file_content = f.read()
            
            file_name = file_path.name
            file_message = {
                "role": "user",
                "content": f"{prompt}\n\nNom du fichier: {file_name}\n\nContenu du fichier:\n\n{file_content}"
            }
            
            # Copier les messages précédents et ajouter le message avec le fichier
            mistral_messages = []
            for msg in messages:
                role = msg["role"]
                if role == "system":
                    mistral_messages.append(ChatMessage(role="system", content=msg["content"]))
                elif role == "user":
                    mistral_messages.append(ChatMessage(role="user", content=msg["content"]))
                elif role == "assistant":
                    mistral_messages.append(ChatMessage(role="assistant", content=msg["content"]))
            
            # Ajouter le message avec le contenu du fichier
            mistral_messages.append(ChatMessage(role="user", content=file_message["content"]))
            
            response = await self.client.chat(
                model=self.model,
                messages=mistral_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens or 4096
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Erreur lors du traitement du fichier: {str(e)}. Mistral ne prend pas en charge nativement l'analyse de fichiers non textuels. Veuillez utiliser un autre fournisseur comme Claude ou GPT pour ce type de fichier."