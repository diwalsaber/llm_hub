"""
Module config - Configuration pour LLM Hub

Ce module centralise les paramètres de configuration pour l'application.
"""

from app.config.settings import (
    BASE_DIR, DATA_DIR, CONVERSATIONS_DIR, UPLOADS_DIR,
    APP_NAME, MAX_HISTORY_LENGTH, ENABLE_AGENTIC_MODE, DEFAULT_TEMPERATURE,
    LLM_PROVIDERS, AVAILABLE_PROVIDERS,
    get_provider_config, is_valid_provider
)

__all__ = [
    'BASE_DIR',
    'DATA_DIR', 
    'CONVERSATIONS_DIR', 
    'UPLOADS_DIR',
    'APP_NAME', 
    'MAX_HISTORY_LENGTH', 
    'ENABLE_AGENTIC_MODE', 
    'DEFAULT_TEMPERATURE',
    'LLM_PROVIDERS', 
    'AVAILABLE_PROVIDERS',
    'get_provider_config', 
    'is_valid_provider'
]