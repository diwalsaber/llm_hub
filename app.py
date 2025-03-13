import os
import asyncio
import tempfile
from typing import Dict, List, Optional, Any

import chainlit as cl
from chainlit.element import Element
from chainlit.action import Action
from chainlit.message import Message

from app.llm_providers import get_llm_provider, BaseLLMProvider
from app.utils.config import settings
from app.utils.conversation import Conversation
from app.utils.file_handler import FileHandler
from app.utils.prompt_templates import PromptTemplateManager, PromptTemplate
from app.agents.llm_agent import LLMAgent, AgentConfig, AgentConversation

# Variables globales pour gérer l'état de l'application
current_conversation: Optional[Conversation] = None
current_provider: Optional[BaseLLMProvider] = None
current_provider_name: Optional[str] = None
current_agent_conversation: Optional[AgentConversation] = None
available_providers = settings.get_available_providers()

# Actions disponibles
ACTIONS = {
    "new_conversation": Action(
        name="new_conversation",
        label="Nouvelle conversation",
        description="Démarrer une nouvelle conversation",
        payload={}
    ),
    "export_conversation": Action(
        name="export_conversation",
        label="Exporter la conversation",
        description="Exporter la conversation au format Markdown",
        payload={}
    ),
    "use_template": Action(
        name="use_template",
        label="Utiliser un template",
        description="Utiliser un template de prompt",
        payload={}
    ),
    "start_agent_mode": Action(
        name="start_agent_mode",
        label="Mode agents",
        description="Démarrer une conversation entre plusieurs agents LLM",
        payload={}
    ),
    "stop_agent_mode": Action(
        name="stop_agent_mode",
        label="Arrêter mode agents",
        description="Arrêter le mode conversation entre agents",
        payload={}
    ),
    "change_provider": Action(
        name="change_provider",
        label="Changer le modèle",
        description="Changer le fournisseur LLM",
        payload={}
    ),
    "use_template_select": Action(
        name="use_template_select",
        label="Sélectionner le template",
        description="Sélectionner un template de prompt",
        payload={}
    )
}

@cl.on_chat_start
async def on_chat_start():
    """Initialisation de la session de chat"""
    global current_conversation, current_provider, current_provider_name

    # Créer une nouvelle conversation
    current_conversation = Conversation()

    # Ajouter un message système par défaut
    default_template = PromptTemplateManager.get_default_system_message()
    system_text = default_template.content if hasattr(default_template, "content") else str(default_template)
    current_conversation.add_message("system", system_text)

    # Récupérer les fournisseurs LLM disponibles
    providers_list = [{"value": name, "label": settings} for name, settings in available_providers.items()]

    # Définir le fournisseur par défaut si disponible
    if "anthropic" in available_providers:
        current_provider_name = "anthropic"
    elif "openai" in available_providers:
        current_provider_name = "openai"
    elif len(available_providers) > 0:
        current_provider_name = list(available_providers.keys())[0]

    if current_provider_name:
        provider_settings = available_providers[current_provider_name]
        current_provider = get_llm_provider(
            current_provider_name,
            provider_settings.api_key,
            provider_settings.model,
            temperature=provider_settings.temperature,
            max_tokens=provider_settings.max_tokens
        )

    # Message de bienvenue
    welcome_message = (
        "Bienvenue sur LLM Hub ! Vous pouvez discuter avec différents modèles en sélectionnant votre fournisseur préféré."
    )
    if len(available_providers) == 0:
        welcome_message += "\n\n⚠️ Aucun fournisseur LLM n'est configuré. Veuillez ajouter vos clés API dans le fichier .env."
    else:
        welcome_message += f"\n\nModèle actuel: {current_provider_name}"

    await cl.Message(content=welcome_message).send()

    # Ajouter les actions disponibles
    await cl.Message(content="").actions(
        [
            ACTIONS["new_conversation"],
            ACTIONS["export_conversation"],
            ACTIONS["use_template"],
            ACTIONS["start_agent_mode"]
        ]
    ).send()

    # Ajouter un sélecteur de modèle si des fournisseurs sont disponibles
    if len(available_providers) > 0:
        settings_list = []
        for name, provider_settings in available_providers.items():
            settings_list.append({
                "value": name,
                "label": f"{name.capitalize()} - {provider_settings.model}"
            })
        await cl.Select(
            id="provider_select",
            label="Sélectionner un modèle LLM",
            values=settings_list,
            initial_value=current_provider_name,
            action=ACTIONS["change_provider"]
        ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """Gestion des messages de l'utilisateur"""
    global current_conversation, current_provider, current_provider_name, current_agent_conversation

    # Si le message contient un payload d'action, le déléguer à handle_action et arrêter le traitement
    action_payload = getattr(message, "payload", None)
    if action_payload and "name" in action_payload:
        await handle_action(action_payload)
        return

    # Vérifier si un fournisseur LLM est disponible
    if current_provider is None:
        await cl.Message(
            content="⚠️ Aucun fournisseur LLM n'est configuré. Veuillez ajouter vos clés API dans le fichier .env."
        ).send()
        return

    # Traiter les fichiers joints, le cas échéant
    files = message.elements
    file_contents = []

    for file in files:
        if file.type == "file":
            # Sauvegarder le fichier
            file_meta = FileHandler.save_uploaded_file(
                file.content,
                file.name,
                current_conversation.id
            )
            # Ajouter une référence au fichier dans la conversation
            current_conversation.add_file_reference(
                file_meta["file_id"],
                file_meta["file_name"],
                file_meta["file_path"]
            )
            # Ajouter au contenu du message
            file_contents.append(f"[Fichier joint: {file_meta['file_name']}]")

    # Ajouter le message de l'utilisateur à la conversation
    user_content = message.content
    if file_contents:
        user_content = f"{user_content}\n\n" + "\n".join(file_contents)
    current_conversation.add_message("user", user_content)

    # Démarrer un message de réponse avec un indicateur de chargement
    msg = cl.Message(content="")
    await msg.send()

    try:
        # Si nous sommes en mode agents
        if current_agent_conversation is not None:
            await current_agent_conversation.add_user_message(message.content)
            agent_messages = await current_agent_conversation.run_turn()
            for agent_msg in agent_messages:
                agent_msg_content = f"**{agent_msg.agent_name}**: {agent_msg.content}"
                await cl.Message(
                    content=agent_msg_content,
                    author=agent_msg.agent_name
                ).send()
            return

        # Traiter les fichiers avec le LLM, le cas échéant
        if files and len(files) == 1:
            file = files[0]
            file_path = FileHandler.get_file_path(
                file_meta["file_id"],
                current_conversation.id
            )
            prompt = (
                f"Voici un fichier appelé '{file.name}'. Pourrais-tu l'analyser et me donner des informations pertinentes à son sujet ? "
                f"{message.content}"
            )
            response = await current_provider.process_file(
                file_path,
                current_conversation.get_messages_for_provider(),
                prompt
            )
        else:
            response = await current_provider.generate(
                current_conversation.get_messages_for_provider()
            )
        await msg.update(content=response)
        current_conversation.add_message(
            "assistant",
            response,
            provider=current_provider_name
        )
    except Exception as e:
        error_message = f"Erreur lors de la génération de la réponse: {str(e)}"
        await msg.update(content=error_message)
        current_conversation.add_message(
            "assistant",
            error_message,
            provider=current_provider_name,
            metadata={"error": True}
        )

async def handle_action(action: dict):
    """
    Gestion des actions de l'utilisateur.
    Cette fonction centralise la logique précédemment gérée par @cl.on_action.
    """
    global current_conversation, current_agent_conversation, current_provider, current_provider_name

    if action.get("name") == "new_conversation":
        current_conversation = Conversation()
        system_message = PromptTemplateManager.get_default_system_message()
        current_conversation.add_message("system", system_message)
        current_agent_conversation = None
        await cl.Message(content="Une nouvelle conversation a été créée.").send()

    elif action.get("name") == "export_conversation":
        if current_conversation:
            markdown = current_conversation.export_markdown()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as tmp:
                tmp.write(markdown.encode("utf-8"))
                tmp_path = tmp.name
            file_element = cl.File(
                name=f"conversation_{current_conversation.id}.md",
                path=tmp_path,
                display="inline"
            )
            await cl.Message(
                content="Voici l'export de votre conversation au format Markdown.",
                elements=[file_element]
            ).send()
            asyncio.create_task(delete_temp_file(tmp_path))

    elif action.get("name") == "use_template":
        templates = PromptTemplateManager.get_all_templates()
        template_options = [
            {"value": template.id, "label": f"{template.name} - {template.category}"}
            for template in templates
        ]
        await cl.Select(
            id="template_select",
            label="Sélectionner un template de prompt",
            values=template_options,
            action=ACTIONS["use_template_select"]
        ).send()

    elif action.get("name") == "change_provider":
        provider_select = cl.user_session.get("provider_select")
        if provider_select and provider_select.value in available_providers:
            new_provider = provider_select.value
            provider_settings = available_providers[new_provider]
            current_provider = get_llm_provider(
                new_provider,
                provider_settings.api_key,
                provider_settings.model,
                temperature=provider_settings.temperature,
                max_tokens=provider_settings.max_tokens
            )
            current_provider_name = new_provider
            await cl.Message(
                content=f"Modèle changé pour: {new_provider.capitalize()} - {provider_settings.model}"
            ).send()

    elif action.get("name") == "use_template_select":
        template_select = cl.user_session.get("template_select")
        if template_select and template_select.value:
            template_id = template_select.value
            template = PromptTemplateManager.get_template_by_id(template_id)
            if template:
                await cl.Message(
                    content=f"Template sélectionné: **{template.name}**\n\n{template.content}"
                ).send()
                if template.system_message:
                    current_conversation.add_message("system", template.system_message)
                    await cl.Message(
                        content="Message système mis à jour pour ce template."
                    ).send()

    elif action.get("name") == "start_agent_mode":
        if len(available_providers) < 2:
            await cl.Message(
                content="⚠️ Le mode agents nécessite au moins deux fournisseurs LLM configurés."
            ).send()
            return
        provider_options = [
            {"value": name, "label": f"{name.capitalize()} - {provider_settings.model}"}
            for name, provider_settings in available_providers.items()
        ]
        await cl.Select(
            id="agent_providers_select",
            label="Sélectionner les fournisseurs pour les agents (ctrl+clic pour sélection multiple)",
            values=provider_options,
            multiple=True
        ).send()
        await cl.AskUserMessage(
            content="Quel est le sujet de la conversation entre les agents ?",
            timeout=180
        ).send()
        topic_response = await cl.AskUserMessage(
            content="Définissez les rôles des agents (un par ligne au format 'Nom: Description du rôle')",
            timeout=180
        ).send()
        providers_select = cl.user_session.get("agent_providers_select")
        if not providers_select or not providers_select.value:
            await cl.Message(
                content="Aucun fournisseur sélectionné. Le mode agents n'a pas pu être démarré."
            ).send()
            return
        selected_providers = providers_select.value
        if isinstance(selected_providers, str):
            selected_providers = [selected_providers]
        topic = cl.user_session.get("last_user_message", "Discussion générale")
        roles_text = topic_response.content
        roles_lines = roles_text.strip().split("\n")
        roles = []
        for line in roles_lines:
            if ":" in line:
                name, description = line.split(":", 1)
                roles.append({
                    "name": name.strip(),
                    "description": description.strip()
                })
        while len(roles) < len(selected_providers):
            roles.append({
                "name": f"Agent {len(roles) + 1}",
                "description": "Un assistant IA utile et informatif"
            })
        agents = []
        for i, provider_name in enumerate(selected_providers):
            if i >= len(roles):
                break
            role = roles[i]
            provider_settings = available_providers[provider_name]
            agent_config = AgentConfig(
                name=role["name"],
                provider_name=provider_name,
                model=provider_settings.model,
                system_message=f"Tu es {role['name']}. {role['description']}",
                temperature=provider_settings.temperature,
                max_tokens=provider_settings.max_tokens
            )
            agent = LLMAgent(
                config=agent_config,
                api_key=provider_settings.api_key
            )
            agents.append(agent)
        current_agent_conversation = AgentConversation(
            agents=agents,
            topic=topic,
            max_turns=10,
            conversation_id=current_conversation.id
        )
        await cl.Message(
            content=f"Mode agents activé avec {len(agents)} participants sur le sujet: {topic}"
        ).send()
        await cl.Message(content="").actions([ACTIONS["stop_agent_mode"]]).send()

    elif action.get("name") == "stop_agent_mode":
        current_agent_conversation = None
        await cl.Message(
            content="Mode agents désactivé. Vous pouvez maintenant discuter normalement avec le modèle sélectionné."
        ).send()
        await cl.Message(content="").actions(
            [
                ACTIONS["new_conversation"],
                ACTIONS["export_conversation"],
                ACTIONS["use_template"],
                ACTIONS["start_agent_mode"]
            ]
        ).send()

async def delete_temp_file(file_path, delay=5):
    """Supprime un fichier temporaire après un délai"""
    await asyncio.sleep(delay)
    try:
        os.remove(file_path)
    except Exception:
        pass