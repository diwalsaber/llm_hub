import json
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from .config import settings

class PromptTemplate(BaseModel):
    """Modèle de données pour les templates de prompts"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    content: str
    category: str
    system_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())

class PromptTemplateManager:
    """Gestionnaire de templates de prompts"""
    
    _templates_file = Path("data/prompt_templates.json")
    _default_templates = [
        {
            "id": "default-system",
            "name": "Message système par défaut",
            "description": "Message système standard pour initialiser une conversation",
            "content": "",
            "category": "système",
            "system_message": "Tu es un assistant IA utile, respectueux et honnête. Réponds toujours au mieux de tes capacités en te basant sur les instructions et le contexte fournis.",
            "metadata": {"default": True}
        },
        {
            "id": "code-python",
            "name": "Développement Python",
            "description": "Template pour le développement d'applications Python",
            "content": "Je travaille sur un projet Python et j'ai besoin d'aide pour {tâche}. \n\nContexte: {contexte}\n\nObjectif: {objectif}\n\nMerci de me fournir du code clair, bien commenté et suivant les bonnes pratiques.",
            "category": "développement",
            "system_message": "Tu es un expert en développement Python. Fournis des solutions efficaces, robustes et bien documentées. Privilégie la lisibilité et les bonnes pratiques. Explique toujours ton raisonnement et les choix techniques effectués.",
            "metadata": {"language": "python"}
        },
        {
            "id": "data-analysis",
            "name": "Analyse de données",
            "description": "Template pour l'analyse de données et la data science",
            "content": "J'ai un ensemble de données concernant {sujet} et je voudrais {objectif}.\n\nDétails des données: {détails}\n\nQuestions spécifiques: {questions}",
            "category": "data science",
            "system_message": "Tu es un data scientist expérimenté. Aide l'utilisateur à analyser ses données en proposant des méthodes appropriées, en expliquant les concepts statistiques pertinents et en suggérant des visualisations efficaces.",
            "metadata": {"domain": "data science"}
        },
        {
            "id": "file-analysis",
            "name": "Analyse de fichier",
            "description": "Template pour l'analyse de fichiers uploadés",
            "content": "Voici un fichier que j'aimerais que tu analyses. Peux-tu me fournir un résumé de son contenu et répondre à ces questions spécifiques:\n\n1. {question1}\n2. {question2}\n3. {question3}",
            "category": "analyse",
            "system_message": "Tu es un expert en analyse de documents. Examine attentivement le fichier fourni et réponds aux questions de l'utilisateur de manière précise et détaillée.",
            "metadata": {"file_types": ["txt", "csv", "json", "pdf"]}
        },
        {
            "id": "agent-conversation",
            "name": "Conversation entre agents",
            "description": "Template pour faire discuter plusieurs LLMs ensemble",
            "content": "Je souhaite que tu joues le rôle de {rôle} dans cette conversation. Tu vas discuter avec d'autres agents IA sur le sujet suivant: {sujet}.\n\nTon objectif est de {objectif}.\n\nContexte: {contexte}",
            "category": "agents",
            "system_message": "Tu es un agent spécialisé qui va participer à une conversation multi-agents. Reste dans ton rôle défini et apporte ton expertise spécifique à la discussion. Sois constructif et collaboratif.",
            "metadata": {"agentic": True}
        }
    ]
    
    @classmethod
    def _ensure_templates_file(cls):
        """Vérifie que le fichier de templates existe, le crée avec les templates par défaut sinon"""
        if not cls._templates_file.exists():
            # Créer le répertoire parent si nécessaire
            cls._templates_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Écrire les templates par défaut
            with open(cls._templates_file, "w", encoding="utf-8") as f:
                json.dump(cls._default_templates, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def get_all_templates(cls) -> List[PromptTemplate]:
        """
        Récupère tous les templates de prompts.
        
        Returns:
            Liste des templates
        """
        cls._ensure_templates_file()
        
        with open(cls._templates_file, "r", encoding="utf-8") as f:
            templates_data = json.load(f)
        
        return [PromptTemplate(**template) for template in templates_data]
    
    @classmethod
    def get_template_by_id(cls, template_id: str) -> Optional[PromptTemplate]:
        """
        Récupère un template par son ID.
        
        Args:
            template_id: ID du template
            
        Returns:
            Le template ou None s'il n'existe pas
        """
        templates = cls.get_all_templates()
        
        for template in templates:
            if template.id == template_id:
                return template
        
        return None
    
    @classmethod
    def get_templates_by_category(cls, category: str) -> List[PromptTemplate]:
        """
        Récupère les templates par catégorie.
        
        Args:
            category: Catégorie des templates
            
        Returns:
            Liste des templates de la catégorie
        """
        templates = cls.get_all_templates()
        return [template for template in templates if template.category.lower() == category.lower()]
    
    @classmethod
    def save_template(cls, template: PromptTemplate) -> PromptTemplate:
        """
        Sauvegarde un template (création ou mise à jour).
        
        Args:
            template: Template à sauvegarder
            
        Returns:
            Le template sauvegardé
        """
        templates = cls.get_all_templates()
        
        # Mise à jour de la date de modification
        template.updated_at = datetime.datetime.now().isoformat()
        
        # Vérifier si c'est une mise à jour ou une création
        for i, existing_template in enumerate(templates):
            if existing_template.id == template.id:
                # Mise à jour
                templates[i] = template
                break
        else:
            # Création
            templates.append(template)
        
        # Sauvegarder tous les templates
        with open(cls._templates_file, "w", encoding="utf-8") as f:
            json.dump([t.dict() for t in templates], f, ensure_ascii=False, indent=2)
        
        return template
    
    @classmethod
    def delete_template(cls, template_id: str) -> bool:
        """
        Supprime un template.
        
        Args:
            template_id: ID du template à supprimer
            
        Returns:
            True si le template a été supprimé, False sinon
        """
        templates = cls.get_all_templates()
        
        # Filtrer les templates pour exclure celui à supprimer
        new_templates = [t for t in templates if t.id != template_id]
        
        # Vérifier si un template a été supprimé
        if len(new_templates) < len(templates):
            with open(cls._templates_file, "w", encoding="utf-8") as f:
                json.dump([t.dict() for t in new_templates], f, ensure_ascii=False, indent=2)
            return True
        
        return False
    
    @classmethod
    def get_default_system_message(cls) -> str:
        """
        Récupère le message système par défaut.
        
        Returns:
            Le message système par défaut
        """
        template = cls.get_template_by_id("default-system")
        
        if template and template.system_message:
            return template