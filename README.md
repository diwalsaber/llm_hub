# LLM Hub

LLM Hub est une interface unifiée permettant d'interagir avec différents modèles de langage (LLMs) comme Claude, ChatGPT, Mistral, et DeepSeek.

![LLM Hub](https://via.placeholder.com/800x450.png?text=LLM+Hub+Interface)

## Caractéristiques

- **Interface unifiée** pour plusieurs modèles de langage (Claude, ChatGPT, Mistral, DeepSeek)
- **Gestion de conversations multiples**
- **Partage de fichiers** avec les LLMs
- **Templates de prompts** prédéfinis et personnalisables
- **Mode agents** permettant de faire discuter plusieurs LLMs entre eux
- **Sauvegarde et export** des conversations
- **Installation facile** avec Docker

## Prérequis

- Python 3.10+
- Clés API pour les modèles que vous souhaitez utiliser:
  - Anthropic (Claude)
  - OpenAI (ChatGPT)
  - Mistral AI
  - DeepSeek

## Installation

### Installation locale

1. Clonez le dépôt:
   ```bash
   git clone https://github.com/votre-repo/llm-hub.git
   cd llm-hub
   ```

2. Créez un environnement virtuel:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. Installez les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

4. Copiez le fichier d'environnement exemple et configurez vos clés API:
   ```bash
   cp app/config/.env.example .env
   # Éditez le fichier .env avec vos clés API
   ```

5. Lancez l'application:
   ```bash
   chainlit run app/app.py
   ```

### Installation avec Docker

1. Clonez le dépôt:
   ```bash
   git clone https://github.com/votre-repo/llm-hub.git
   cd llm-hub
   ```

2. Copiez le fichier d'environnement exemple et configurez vos clés API:
   ```bash
   cp app/config/.env.example .env
   # Éditez le fichier .env avec vos clés API
   ```

3. Construisez et lancez le conteneur Docker:
   ```bash
   docker-compose up -d
   ```

4. Accédez à l'application à l'adresse http://localhost:8000

## Usage

### Conversation standard

1. Sélectionnez un modèle LLM dans la liste déroulante
2. Tapez votre message dans la zone de texte
3. Utilisez les boutons d'action pour:
   - Créer une nouvelle conversation
   - Exporter la conversation actuelle
   - Utiliser des templates de prompts
   - Démarrer le mode agents

### Partage de fichiers

1. Faites glisser-déposer un fichier dans la zone de chat
2. Le LLM analysera le contenu du fichier
3. Les fichiers sont sauvegardés et peuvent être référencés ultérieurement

### Mode agents

1. Cliquez sur le bouton "Mode agents"
2. Sélectionnez les fournisseurs LLM que vous souhaitez utiliser
3. Définissez le sujet de la conversation
4. Définissez les rôles des différents agents
5. Laissez les LLMs converser entre eux
6. Vous pouvez intervenir à tout moment en envoyant un message

## Structure du projet

```
llm-hub/
├── app/
│   ├── llm_providers/   # Interfaces avec les différents fournisseurs LLM
│   ├── utils/           # Utilities (config, conversation, fichiers)
│   ├── agents/          # Fonctionnalités pour le mode agents
│   ├── config/          # Fichiers de configuration
│   ├── static/          # Ressources statiques (CSS, images)
│   ├── chainlit.md      # Page d'accueil Chainlit
│   └── app.py           # Point d'entrée de l'application
├── tests/               # Tests unitaires
├── data/                # Données persistantes (conversations, uploads)
├── Dockerfile           # Configuration Docker
├── docker-compose.yml   # Configuration Docker Compose
└── requirements.txt     # Dépendances Python
```

## Personnalisation

### Ajouter de nouveaux templates de prompts

Les templates de prompts sont stockés dans le fichier `data/prompt_templates.json`. Vous pouvez en ajouter de nouveaux directement via l'interface ou en modifiant ce fichier.

### Ajouter un nouveau fournisseur LLM

1. Créez un nouveau fichier dans `app/llm_providers/`
2. Implémentez la classe provider en héritant de `BaseLLMProvider`
3. Ajoutez le nouveau provider dans la factory dans `app/llm_providers/__init__.py`
4. Ajoutez les paramètres de configuration dans `.env.example`

## Contribution

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer:

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez sur la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## Contact

Votre Nom - [@votre_twitter](https://twitter.com/votre_twitter) - email@example.com

Lien du projet: [https://github.com/votre-repo/llm-hub](https://github.com/votre-repo/llm-hub)