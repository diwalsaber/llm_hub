import asyncio
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
import datetime
import uuid

from app.llm_providers import BaseLLMProvider, get_llm_provider
from app.utils.conversation import Conversation
from app.utils.config import settings

class AgentConfig(BaseModel):
    """Configuration d'un agent LLM"""
    name: str
    provider_name: str
    model: str
    system_message: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentMessage(BaseModel):
    """Message dans une conversation entre agents"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LLMAgent:
    """
    Agent basé sur un LLM qui peut interagir avec d'autres agents
    """
    
    def __init__(self, config: AgentConfig, api_key: str):
        self.config = config
        self.provider = get_llm_provider(
            config.provider_name,
            api_key,
            config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        self.history: List[AgentMessage] = []
    
    async def respond(self, conversation_history: List[AgentMessage], topic: str) -> AgentMessage:
        """
        Génère une réponse de l'agent basée sur l'historique de la conversation.
        
        Args:
            conversation_history: Historique de la conversation entre agents
            topic: Sujet de la conversation
            
        Returns:
            Message généré par l'agent
        """
        # Formater l'historique des messages pour le fournisseur LLM
        messages = []
        
        # Ajouter le message système avec les instructions pour l'agent
        messages.append({
            "role": "system",
            "content": f"{self.config.system_message}\n\nSujet de discussion: {topic}\n\nTu es '{self.config.name}'. Réponds de manière concise et pertinente en tenant compte des messages précédents."
        })
        
        # Ajouter l'historique de la conversation
        for msg in conversation_history:
            messages.append({
                "role": "user" if msg.agent_name != self.config.name else "assistant",
                "content": f"{msg.agent_name}: {msg.content}"
            })
        
        # Générer la réponse
        response = await self.provider.generate(messages, temperature=self.config.temperature)
        
        # Créer le message de l'agent
        agent_message = AgentMessage(
            agent_name=self.config.name,
            content=response,
            metadata={
                "provider": self.config.provider_name,
                "model": self.config.model,
                "temperature": self.config.temperature
            }
        )
        
        # Ajouter à l'historique de l'agent
        self.history.append(agent_message)
        
        return agent_message

class AgentConversation:
    """
    Gère une conversation entre plusieurs agents LLM
    """
    
    def __init__(
        self, 
        agents: List[LLMAgent],
        topic: str,
        max_turns: int = 10,
        conversation_id: Optional[str] = None
    ):
        self.agents = agents
        self.topic = topic
        self.max_turns = max_turns
        self.history: List[AgentMessage] = []
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.conversation = Conversation(
            id=self.conversation_id,
            title=f"Conversation multi-agents: {topic}",
            metadata={
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
                "topic": topic,
                "agents": [agent.config.name for agent in agents],
                "providers": [agent.config.provider_name for agent in agents],
                "max_turns": max_turns
            }
        )
    
    async def add_user_message(self, content: str) -> None:
        """
        Ajoute un message de l'utilisateur à la conversation.
        
        Args:
            content: Contenu du message
        """
        user_message = AgentMessage(
            agent_name="Utilisateur",
            content=content
        )
        
        self.history.append(user_message)
        self.conversation.add_message("user", content)
    
    async def run_turn(self) -> List[AgentMessage]:
        """
        Exécute un tour de la conversation où chaque agent répond une fois.
        
        Returns:
            Liste des messages générés par les agents
        """
        messages = []
        
        for agent in self.agents:
            try:
                agent_message = await agent.respond(self.history, self.topic)
                self.history.append(agent_message)
                messages.append(agent_message)
                
                # Ajouter le message à la conversation Chainlit
                self.conversation.add_message(
                    "assistant", 
                    agent_message.content, 
                    provider=agent.config.name
                )
            except Exception as e:
                error_message = f"Erreur lors de la génération d'une réponse par {agent.config.name}: {str(e)}"
                print(error_message)
                
                # Ajouter un message d'erreur à l'historique
                error_agent_message = AgentMessage(
                    agent_name=agent.config.name,
                    content=f"[Erreur de génération]",
                    metadata={"error": str(e)}
                )
                self.history.append(error_agent_message)
                messages.append(error_agent_message)
                
                # Ajouter le message d'erreur à la conversation Chainlit
                self.conversation.add_message(
                    "assistant", 
                    error_message, 
                    provider=agent.config.name,
                    metadata={"error": True}
                )
        
        return messages
    
    async def run_conversation(self, initial_message: Optional[str] = None) -> List[AgentMessage]:
        """
        Exécute la conversation complète entre les agents.
        
        Args:
            initial_message: Message initial pour démarrer la conversation (optionnel)
            
        Returns:
            Historique complet de la conversation
        """
        # Ajouter un message initial si fourni
        if initial_message:
            await self.add_user_message(initial_message)
        
        # Exécuter la conversation pour le nombre maximum de tours
        for _ in range(self.max_turns):
            await self.run_turn()
            
            # Pause entre les tours pour éviter de surcharger les API
            await asyncio.sleep(1)
        
        return self.history
    
    def get_conversation(self) -> Conversation:
        """
        Retourne l'objet Conversation associé.
        
        Returns:
            Objet Conversation
        """
        return self.conversation