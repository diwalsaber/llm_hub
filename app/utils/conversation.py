import json
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from app.utils.config import settings

class Conversation:
    """Classe représentant une conversation avec un ou plusieurs LLMs"""
    
    def __init__(
        self, 
        id: Optional[str] = None,
        title: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.title = title or f"Nouvelle conversation {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.messages = messages or []
        self.metadata = metadata or {
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "providers_used": [],
            "file_references": []
        }
    
    def add_message(self, role: str, content: str, provider: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ajoute un message à la conversation.
        
        Args:
            role: Rôle du message ("user", "assistant", "system")
            content: Contenu du message
            provider: Nom du fournisseur LLM (pour les messages d'assistant)
            metadata: Métadonnées supplémentaires pour le message
            
        Returns:
            Le message créé
        """
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if provider:
            message["provider"] = provider
            if provider not in self.metadata["providers_used"]:
                self.metadata["providers_used"].append(provider)
        
        if metadata:
            message["metadata"] = metadata
        
        self.messages.append(message)
        self.metadata["updated_at"] = datetime.datetime.now().isoformat()
        
        # Sauvegarder la conversation après chaque ajout de message
        self.save()
        
        return message
    
    def get_messages_for_provider(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Retourne les messages formatés pour être envoyés à un fournisseur LLM.
        
        Args:
            include_system: Si les messages système doivent être inclus
            
        Returns:
            Liste de messages formatés
        """
        provider_messages = []
        
        for msg in self.messages:
            if msg["role"] == "system" and not include_system:
                continue
            
            # Convertir au format simplifié pour les fournisseurs LLM
            provider_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return provider_messages
    
    def add_file_reference(self, file_id: str, file_name: str, file_path: str) -> None:
        """
        Ajoute une référence à un fichier utilisé dans la conversation.
        
        Args:
            file_id: ID unique du fichier
            file_name: Nom original du fichier
            file_path: Chemin vers le fichier stocké
        """
        self.metadata["file_references"].append({
            "file_id": file_id,
            "file_name": file_name,
            "file_path": file_path,
            "added_at": datetime.datetime.now().isoformat()
        })
        self.metadata["updated_at"] = datetime.datetime.now().isoformat()
        self.save()
    
    def save(self) -> None:
        """Sauvegarde la conversation dans un fichier JSON"""
        conversation_path = settings.conversations_dir / f"{self.id}.json"
        
        with open(conversation_path, "w", encoding="utf-8") as f:
            json.dump({
                "id": self.id,
                "title": self.title,
                "messages": self.messages,
                "metadata": self.metadata
            }, f, ensure_ascii=False, indent=2)
    
    def export_markdown(self) -> str:
        """
        Exporte la conversation au format Markdown.
        
        Returns:
            Contenu Markdown de la conversation
        """
        markdown = f"# {self.title}\n\n"
        markdown += f"*Créée le {self.metadata['created_at']}*\n\n"
        
        if self.metadata["providers_used"]:
            markdown += f"*Modèles utilisés: {', '.join(self.metadata['providers_used'])}*\n\n"
        
        markdown += "---\n\n"
        
        for msg in self.messages:
            if msg["role"] == "system":
                markdown += f"**Instructions système:**\n\n"
            elif msg["role"] == "user":
                markdown += f"**Utilisateur:**\n\n"
            elif msg["role"] == "assistant":
                provider = msg.get("provider", "Assistant")
                markdown += f"**{provider}:**\n\n"
            
            markdown += f"{msg['content']}\n\n"
            markdown += "---\n\n"
        
        return markdown
    
    @classmethod
    def load(cls, conversation_id: str) -> "Conversation":
        """
        Charge une conversation depuis un fichier JSON.
        
        Args:
            conversation_id: ID de la conversation à charger
            
        Returns:
            Instance de Conversation
        """
        conversation_path = settings.conversations_dir / f"{conversation_id}.json"
        
        if not conversation_path.exists():
            raise FileNotFoundError(f"Conversation {conversation_id} non trouvée")
        
        with open(conversation_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return cls(
            id=data["id"],
            title=data["title"],
            messages=data["messages"],
            metadata=data["metadata"]
        )
    
    @classmethod
    def list_conversations(cls) -> List[Dict[str, Any]]:
        """
        Liste toutes les conversations disponibles.
        
        Returns:
            Liste des métadonnées des conversations
        """
        conversations = []
        
        for path in settings.conversations_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                conversations.append({
                    "id": data["id"],
                    "title": data["title"],
                    "created_at": data["metadata"]["created_at"],
                    "updated_at": data["metadata"]["updated_at"],
                    "message_count": len(data["messages"]),
                    "providers_used": data["metadata"]["providers_used"]
                })
            except Exception as e:
                print(f"Erreur lors du chargement de {path}: {e}")
        
        # Trier par date de mise à jour (la plus récente en premier)
        return sorted(conversations, key=lambda x: x["updated_at"], reverse=True)