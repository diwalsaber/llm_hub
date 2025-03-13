import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class LLMProviderSettings(BaseSettings):
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    @validator('api_key')
    def api_key_must_not_be_empty(cls, v):
        if not v or v.startswith('your_'):
            return None
        return v

class AppSettings(BaseSettings):
    # Paramètres de l'application
    app_name: str = Field(default="LLM Hub", env="APP_NAME")
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    conversations_dir: Path = Field(default=Path("./data/conversations"), env="CONVERSATIONS_DIR")
    uploads_dir: Path = Field(default=Path("./data/uploads"), env="UPLOADS_DIR")
    max_history_length: int = Field(default=100, env="MAX_HISTORY_LENGTH")
    enable_agentic_mode: bool = Field(default=True, env="ENABLE_AGENTIC_MODE")
    default_temperature: float = Field(default=0.7, env="DEFAULT_TEMPERATURE")
    
    # Configuration des modèles LLM
    anthropic: LLMProviderSettings = LLMProviderSettings(
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        model=os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219"),
    )
    
    openai: LLMProviderSettings = LLMProviderSettings(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model=os.getenv("OPENAI_MODEL", "gpt-4-0125-preview"),
    )
    
    mistral: LLMProviderSettings = LLMProviderSettings(
        api_key=os.getenv("MISTRAL_API_KEY", ""),
        model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
    )
    
    deepseek: LLMProviderSettings = LLMProviderSettings(
        api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-r1-latest"),
    )
    
    def get_available_providers(self) -> Dict[str, LLMProviderSettings]:
        """Retourne un dictionnaire des fournisseurs LLM disponibles (avec API keys configurées)"""
        providers = {}
        
        if self.anthropic.api_key:
            providers["anthropic"] = self.anthropic
            
        if self.openai.api_key:
            providers["openai"] = self.openai
            
        if self.mistral.api_key:
            providers["mistral"] = self.mistral
            
        if self.deepseek.api_key:
            providers["deepseek"] = self.deepseek
            
        return providers
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instance singleton des paramètres de l'application
settings = AppSettings()

# Création des répertoires nécessaires
def ensure_directories():
    settings.data_dir.mkdir(exist_ok=True)
    settings.conversations_dir.mkdir(exist_ok=True)
    settings.uploads_dir.mkdir(exist_ok=True)

ensure_directories()