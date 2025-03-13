import os
import uuid
import shutil
import mimetypes
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from .config import settings

class FileHandler:
    """Gestionnaire de fichiers pour l'application"""
    
    @staticmethod
    def save_uploaded_file(file_content: bytes, file_name: str, conversation_id: Optional[str] = None) -> Dict[str, str]:
        """
        Sauvegarde un fichier téléchargé.
        
        Args:
            file_content: Contenu binaire du fichier
            file_name: Nom original du fichier
            conversation_id: ID de la conversation associée (optionnel)
            
        Returns:
            Métadonnées du fichier
        """
        # Générer un ID unique pour le fichier
        file_id = str(uuid.uuid4())
        
        # Créer un dossier spécifique à la conversation si nécessaire
        if conversation_id:
            upload_dir = settings.uploads_dir / conversation_id
            upload_dir.mkdir(exist_ok=True)
        else:
            upload_dir = settings.uploads_dir
        
        # Déterminer l'extension du fichier
        _, extension = os.path.splitext(file_name)
        
        # Construire le chemin de sauvegarde
        save_path = upload_dir / f"{file_id}{extension}"
        
        # Sauvegarder le fichier
        with open(save_path, "wb") as f:
            f.write(file_content)
        
        # Déterminer le type MIME
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # Retourner les métadonnées
        return {
            "file_id": file_id,
            "file_name": file_name,
            "file_path": str(save_path),
            "mime_type": mime_type,
            "size": len(file_content),
            "conversation_id": conversation_id
        }
    
    @staticmethod
    def get_file_path(file_id: str, conversation_id: Optional[str] = None) -> Optional[Path]:
        """
        Récupère le chemin d'un fichier à partir de son ID.
        
        Args:
            file_id: ID du fichier
            conversation_id: ID de la conversation associée (optionnel)
            
        Returns:
            Chemin du fichier ou None si non trouvé
        """
        if conversation_id:
            upload_dir = settings.uploads_dir / conversation_id
        else:
            upload_dir = settings.uploads_dir
        
        # Rechercher le fichier avec l'ID spécifié (quelle que soit l'extension)
        for path in upload_dir.glob(f"{file_id}*"):
            return path
        
        return None
    
    @staticmethod
    def delete_file(file_id: str, conversation_id: Optional[str] = None) -> bool:
        """
        Supprime un fichier.
        
        Args:
            file_id: ID du fichier
            conversation_id: ID de la conversation associée (optionnel)
            
        Returns:
            True si le fichier a été supprimé, False sinon
        """
        file_path = FileHandler.get_file_path(file_id, conversation_id)
        
        if file_path and file_path.exists():
            os.remove(file_path)
            return True
        
        return False
    
    @staticmethod
    def get_conversation_files(conversation_id: str) -> List[Dict[str, str]]:
        """
        Récupère la liste des fichiers associés à une conversation.
        
        Args:
            conversation_id: ID de la conversation
            
        Returns:
            Liste des métadonnées des fichiers
        """
        upload_dir = settings.uploads_dir / conversation_id
        
        if not upload_dir.exists():
            return []
        
        files = []
        
        for path in upload_dir.glob("*"):
            file_id = path.stem
            file_name = path.name
            mime_type, _ = mimetypes.guess_type(file_name)
            
            if mime_type is None:
                mime_type = "application/octet-stream"
            
            files.append({
                "file_id": file_id,
                "file_name": file_name,
                "file_path": str(path),
                "mime_type": mime_type,
                "size": path.stat().st_size,
                "conversation_id": conversation_id
            })
        
        return files
    
    @staticmethod
    def is_image(file_path: Path) -> bool:
        """
        Vérifie si un fichier est une image.
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            True si le fichier est une image, False sinon
        """
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type is not None and mime_type.startswith("image/")
    
    @staticmethod
    def is_text(file_path: Path) -> bool:
        """
        Vérifie si un fichier est un fichier texte.
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            True si le fichier est un texte, False sinon
        """
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type is not None and (
            mime_type.startswith("text/") or
            mime_type in ["application/json", "application/xml", "application/csv"]
        )
    
    @staticmethod
    def get_file_preview(file_path: Path, max_length: int = 1000) -> Tuple[str, bool]:
        """
        Récupère un aperçu du contenu d'un fichier texte.
        
        Args:
            file_path: Chemin du fichier
            max_length: Nombre maximum de caractères à retourner
            
        Returns:
            Tuple contenant l'aperçu et un booléen indiquant si le texte a été tronqué
        """
        if not FileHandler.is_text(file_path):
            return "[Ce fichier n'est pas un fichier texte]", False
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(max_length + 1)
            
            if len(content) > max_length:
                return content[:max_length], True
            else:
                return content, False
        
        except Exception as e:
            return f"[Erreur lors de la lecture du fichier: {str(e)}]", False