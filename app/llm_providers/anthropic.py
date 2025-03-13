from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Union
import os
from pathlib import Path

class BaseLLMProvider(ABC):
    """Classe de base pour tous les fournisseurs de LLM"""
    
    name: str
    model: str
    temperature: float
    max_tokens: Optional[int]
    
    def __init__(
        self, 
        api_key: str, 
        model: str, 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    @abstractmethod
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, Any]:
        """
        Génère une réponse à partir d'une liste de messages.
        
        Args:
            messages: Liste des messages précédents dans la conversation
            temperature: Valeur de température pour la génération (optionnel)
            max_tokens: Nombre maximum de tokens à générer (optionnel)
            stream: Si True, retourne un générateur qui produit des tokens un par un
            
        Returns:
            Réponse du modèle sous forme de string ou un générateur si stream=True
        """
        pass
    
    @abstractmethod
    async def process_file(
        self, 
        file_path: Path, 
        messages: List[Dict[str, str]],
        prompt: str
    ) -> str:
        """
        Traite un fichier avec le LLM.
        
        Args:
            file_path: Chemin vers le fichier à traiter
            messages: Contexte de la conversation (optionnel)
            prompt: Instructions pour le traitement du fichier
            
        Returns:
            Réponse du modèle après traitement du fichier
        """
        pass

# Factory pour obtenir le fournisseur LLM approprié
def get_llm_provider(provider_name: str, api_key: str, model: str, **kwargs) -> BaseLLMProvider:
    """
    Retourne l'instance du fournisseur LLM demandé.
    
    Args:
        provider_name: Nom du fournisseur ('anthropic', 'openai', 'mistral', 'deepseek')
        api_key: Clé API pour le fournisseur
        model: Nom du modèle à utiliser
        **kwargs: Paramètres supplémentaires pour le fournisseur
        
    Returns:
        Instance du fournisseur LLM
    """
    if provider_name == "anthropic":
        from .anthropic import AnthropicProvider
        return AnthropicProvider(api_key, model, **kwargs)
    
    elif provider_name == "openai":
        from .openai import OpenAIProvider
        return OpenAIProvider(api_key, model, **kwargs)
    
    elif provider_name == "mistral":
        from .mistral import MistralProvider
        return MistralProvider(api_key, model, **kwargs)
    
    elif provider_name == "deepseek":
        from .deepseek import DeepSeekProvider
        return DeepSeekProvider(api_key, model, **kwargs)
    
    else:
        raise ValueError(f"Fournisseur LLM non reconnu: {provider_name}")
    