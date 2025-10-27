# 🤖 Chatbot RAG IA GEN

Un chatbot **RAG (Retrieval-Augmented Generation)** qui permet d’interroger vos documents (PDF / pages web) et d’obtenir des réponses contextuelles grâce à l’IA générative.

---

## Démo rapide (Gradio)

```bash
git clone https://github.com/Momo3972/chatbot-rag-ia-gen.git
cd chatbot-rag-ia-gen

# (optionnel) créer un venv
python -m venv .venv && .\.venv\Scripts\Activate.ps1
# ou: source .venv/bin/activate (macOS/Linux)

pip install -r requirements.txt
# Créez le fichier .env (non versionné)
echo OPENAI_API_KEY=sk-... > .env

# Lancez la démo web locale
python app_gradio.py
```

Ouvrez l’URL indiquée par Gradio. Chargez un **PDF** ou une **URL**, puis posez vos questions dans le chatbot.

---

## Architecture (vue simple)

```text
PDF / URL  →  extraction texte  →  chunks  →  embeddings (OpenAI)  →  similarité  →  LLM  →  réponse
```

- **Extraction** : `PyPDF2` pour les PDF, `requests + BeautifulSoup` pour les pages web
- **Embeddings** : modèle `text-embedding-ada-002`
- **Similarity** : cosinus
- **Génération** : `gpt-3.5-turbo` (modifiable)

---

## Installation (détail)

1) **Cloner & venv**
```bash
git clone https://github.com/Momo3972/chatbot-rag-ia-gen.git
cd chatbot-rag-ia-gen
python -m venv .venv && .\.venv\Scripts\Activate.ps1
```

2) **Dépendances**
```bash
pip install -r requirements.txt
```

3) **Clé OpenAI**
Créez un fichier `.env` à la racine (voir `.env.example`) :
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

4) **Lancer la démo**
```bash
python app_gradio.py
```

---

## Structure
```text
.
chatbot-rag-ia-gen/
├── .env.example
├── .gitignore
├── .venv/
├── app_gradio.py        ← ton app web Gradio
├── Chatbot_RAG.ipynb    ← ton notebook explicatif
├── README.md            ← documentation claire
├── requirements.txt     ← dépendances “runtime” (pour exécuter l’app)
└── requirements-dev.txt ← dépendances “dev” (pour bosser dans VS Code / Jupyter)
```

---

## Config & Modèles
- Modèle d’embeddings : `text-embedding-ada-002`
- Modèle de chat : `gpt-3.5-turbo` (modifiable dans `app_gradio.py` → `RAGChatbot.ask`)

---

## Sécurité
- **Ne commitez jamais** votre vraie clé : elle doit rester dans `.env` (déjà ignoré).
- En cas d’alerte GitHub “secret scanning”, remplacez la clé côté OpenAI (rotation).

---

## Auteur
**Mohamed Lamine OULD BOUYA** – Projet portfolio Big Data & IA
