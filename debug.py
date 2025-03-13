"""
Script de diagnostic pour LLM Hub
Ce script effectue une série de tests pour vérifier l'installation et identifier les problèmes.
"""

import os
import sys
import importlib
import pkg_resources

def check_imports():
    """Vérifie les importations des modules principaux"""
    modules = [
        "chainlit",
        "anthropic",
        "openai",
        "mistralai",
        "pydantic",
        "pydantic_settings",
        "dotenv"
    ]
    
    print("== Test des importations de modules ==")
    for module in modules:
        try:
            importlib.import_module(module)
            version = pkg_resources.get_distribution(module).version
            print(f"✓ {module} (version {version})")
        except ImportError:
            print(f"✗ {module} - Module non trouvé. Essayez: pip install {module}")
        except Exception as e:
            print(f"? {module} - {str(e)}")
    print()

def check_app_imports():
    """Vérifie les importations spécifiques à l'application"""
    print("== Test des importations de l'application ==")
    
    # Vérifier l'importation de la classe Action de chainlit
    try:
        from chainlit.action import Action
        action = Action(name="test", label="Test", description="Test action", payload={})
        print("✓ chainlit.action.Action")
    except Exception as e:
        print(f"✗ chainlit.action.Action - {str(e)}")
    
    # Vérifier les importations de notre application
    try:
        import app
        print("✓ app")
    except Exception as e:
        print(f"✗ app - {str(e)}")
    
    try:
        from app.utils.config import settings
        print("✓ app.utils.config.settings")
    except Exception as e:
        print(f"✗ app.utils.config.settings - {str(e)}")
    
    try:
        from app.utils.conversation import Conversation
        print("✓ app.utils.conversation.Conversation")
    except Exception as e:
        print(f"✗ app.utils.conversation.Conversation - {str(e)}")
    
    try:
        from app.llm_providers import BaseLLMProvider, get_llm_provider
        print("✓ app.llm_providers.BaseLLMProvider")
    except Exception as e:
        print(f"✗ app.llm_providers - {str(e)}")
    print()

def check_filesystem():
    """Vérifie l'existence des fichiers et répertoires essentiels"""
    print("== Test du système de fichiers ==")
    
    # Répertoires essentiels
    directories = [
        ".",
        "app",
        "app/llm_providers",
        "app/utils",
        "app/agents",
        "app/config",
        "data",
        "data/conversations",
        "data/uploads"
    ]
    
    for directory in directories:
        if os.path.isdir(directory):
            print(f"✓ Répertoire {directory}")
            # Vérifier la présence de __init__.py dans les packages Python
            if directory.startswith("app") and not os.path.exists(f"{directory}/__init__.py"):
                print(f"✗ {directory}/__init__.py manquant")
        else:
            print(f"✗ Répertoire {directory} introuvable")
    
    # Fichiers essentiels
    files = [
        "app.py",
        "chainlit.md",
        "requirements.txt",
        "app/utils/conversation.py",
        "app/utils/config.py",
        "app/llm_providers/__init__.py"
    ]
    
    for file in files:
        if os.path.isfile(file):
            print(f"✓ Fichier {file}")
        else:
            print(f"✗ Fichier {file} introuvable")
    print()

def check_environment():
    """Vérifie les variables d'environnement et le PYTHONPATH"""
    print("== Test de l'environnement ==")
    
    pythonpath = os.environ.get("PYTHONPATH", "")
    if pythonpath:
        print(f"✓ PYTHONPATH = {pythonpath}")
    else:
        print("✗ PYTHONPATH non défini")
    
    print(f"✓ Répertoire de travail = {os.getcwd()}")
    print(f"✓ Python executable = {sys.executable}")
    print(f"✓ Python version = {sys.version}")
    print()

def main():
    """Fonction principale"""
    print("=== Diagnostic de LLM Hub ===\n")
    
    check_environment()
    check_filesystem()
    check_imports()
    check_app_imports()
    
    print("\n=== Diagnostic terminé ===")
    
    print("\nSi vous rencontrez des problèmes, essayez ces actions :")
    print("1. Vérifiez que tous les fichiers __init__.py sont présents")
    print("2. Installez les dépendances manquantes : pip install -r requirements.txt")
    print("3. Assurez-vous que PYTHONPATH contient le répertoire courant : export PYTHONPATH=$PYTHONPATH:.")
    print("4. Essayez de lancer l'application minimale : chainlit run test_app.py")
    print("5. Si tout échoue, reconstruisez l'image Docker : docker-compose build --no-cache")

if __name__ == "__main__":
    main()