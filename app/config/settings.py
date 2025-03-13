"""
Module de configuration centralisée pour LLM Hub

Ce module agrège tous les paramètres de configuration pour l'application,
en chargeant les variables d'environnement et en définissant des valeurs par défaut.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env si le fichier existe
env_path = Path('.env')
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = os.getenv('DATA_DIR', BASE_DIR / 'data')
CONVERSATIONS_DIR = os.getenv('CONVERSATIONS_DIR', Path(DATA_DIR) / 'conversations')
UPLOADS_DIR = os.getenv('UPLOADS_DIR', Path(DATA_DIR) / 'uploads')

# Paramètres de l'application
APP_NAME = os.getenv('APP_NAME', 'LLM Hub')
MAX_HISTORY_LENGTH = int(os.getenv('MAX_HISTORY_LENGTH', '100'))
ENABLE_AGENTIC_MODE = os.getenv('ENABLE_AGENTIC_MODE', 'true').lower() == 'true'
DEFAULT_TEMPERATURE = float(os.getenv('DEFAULT_TEMPERATURE', '0.7'))

# Paramètres des modèles LLM
LLM_PROVIDERS = {
    'anthropic': {
        'api_key': os.getenv('ANTHROPIC_API_KEY', ''),
        'model': os.getenv('ANTHROPIC_MODEL', 'claude-3-7-sonnet-20250219'),
        'temperature': float(os.getenv('ANTHROPIC_TEMPERATURE', str(DEFAULT_TEMPERATURE))),
        'max_tokens': int(os.getenv('ANTHROPIC_MAX_TOKENS', '4096')) if os.getenv('ANTHROPIC_MAX_TOKENS') else None
    },
    'openai': {
        'api_key': os.getenv('OPENAI_API_KEY', ''),
        'model': os.getenv('OPENAI_MODEL', 'gpt-4-0125-preview'),
        'temperature': float(os.getenv('OPENAI_TEMPERATURE', str(DEFAULT_TEMPERATURE))),
        'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '4096')) if os.getenv('OPENAI_MAX_TOKENS') else None
    },
    'mistral': {
        'api_key': os.getenv('MISTRAL_API_KEY', ''),
        'model': os.getenv('MISTRAL_MODEL', 'mistral-large-latest'),
        'temperature': float(os.getenv('MISTRAL_TEMPERATURE', str(DEFAULT_TEMPERATURE))),
        'max_tokens': int(os.getenv('MISTRAL_MAX_TOKENS', '4096')) if os.getenv('MISTRAL_MAX_TOKENS') else None
    },
    'deepseek': {
        'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
        'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-r1-latest'),
        'temperature': float(os.getenv('DEEPSEEK_TEMPERATURE', str(DEFAULT_TEMPERATURE))),
        'max_tokens': int(os.getenv('DEEPSEEK_MAX_TOKENS', '4096')) if os.getenv('DEEPSEEK_MAX_TOKENS') else None
    }
}

# Filtrer les fournisseurs sans clé API
AVAILABLE_PROVIDERS = {
    name: config for name, config in LLM_PROVIDERS.items() 
    if config['api_key'] and not config['api_key'].startswith('your_')
}

# Paramètres Chainlit
CHAINLIT_AUTH_SECRET = os.getenv('CHAINLIT_AUTH_SECRET', '')
CHAINLIT_MAX_MESSAGE_SIZE = int(os.getenv('CHAINLIT_MAX_MESSAGE_SIZE', '16000'))
CHAINLIT_SERVER_PORT = int(os.getenv('CHAINLIT_PORT', '8000'))
CHAINLIT_SERVER_HOST = os.getenv('CHAINLIT_HOST', '0.0.0.0')

# Paramètres de fichiers
ALLOWED_UPLOAD_EXTENSIONS = [
    '.txt', '.pdf', '.doc', '.docx', '.csv', '.xls', '.xlsx',
    '.json', '.xml', '.md', '.html', '.htm', '.py', '.js',
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'
]
MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', '10'))  # 10 MB par défaut
MAX_UPLOADS_PER_CONVERSATION = int(os.getenv('MAX_UPLOADS_PER_CONVERSATION', '5'))

# Créer les répertoires nécessaires s'ils n'existent pas
Path(DATA_DIR).mkdir(exist_ok=True, parents=True)
Path(CONVERSATIONS_DIR).mkdir(exist_ok=True, parents=True)
Path(UPLOADS_DIR).mkdir(exist_ok=True, parents=True)

def get_provider_config(provider_name: str) -> Optional[Dict[str, Any]]:
    """
    Récupère la configuration d'un fournisseur LLM spécifique.
    
    Args:
        provider_name: Nom du fournisseur ('anthropic', 'openai', etc.)
        
    Returns:
        Configuration du fournisseur ou None s'il n'existe pas
    """
    return AVAILABLE_PROVIDERS.get(provider_name)

def is_valid_provider(provider_name: str) -> bool:
    """
    Vérifie si un fournisseur LLM est valide et configuré.
    
    Args:
        provider_name: Nom du fournisseur à vérifier
        
    Returns:
        True si le fournisseur est valide et configuré, False sinon
    """
    return provider_name in AVAILABLE_PROVIDERS