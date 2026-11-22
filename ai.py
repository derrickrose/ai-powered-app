"""Accès centralisé aux modèles d'IA utilisés dans le workshop.

- openai()            : LLM cloud (GPT) — le plus capable, payant, les données sortent.
- ollama()            : LLM local via Ollama — gratuit, privé, moins capable.
- prompt_openai()     : appelle OpenAI avec un prompt stocké dans prompts/<nom>.yaml
                        (remplace l'ancien pezzo_openai() : le service Pezzo n'est plus utilisé).
- embeddings_openai() : transforme un texte en vecteur (step 4).

Les modèles se configurent dans .env (voir .env.example).
"""
import os
import re

import requests
import yaml
from openai import OpenAI

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_SMALL_MODEL = os.environ.get("OLLAMA_SMALL_MODEL", "llama3.2:1b")
OLLAMA_MEDIUM_MODEL = os.environ.get("OLLAMA_MEDIUM_MODEL", "llama3.2:3b")
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")

_client = None


def _openai_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client


def _chat(messages, model=None, **settings):
    # On n'envoie que les paramètres définis (temperature=None ferait une erreur côté API)
    params = {k: v for k, v in settings.items() if v is not None}
    response = _openai_client().chat.completions.create(
        model=model or OPENAI_MODEL,
        messages=messages,
        **params,
    )
    return response.choices[0].message.content


# ---------------------------
# LLM CLOUD (OpenAI)
# ---------------------------
def openai(prompt, model=None, temperature=None, **settings):
    """Envoie un prompt simple à OpenAI. settings : max_tokens, top_p, ..."""
    return _chat([{"role": "user", "content": prompt}], model=model, temperature=temperature, **settings)


# ---------------------------
# LLM LOCAL (Ollama)
# ---------------------------
def ollama(prompt, model=None, format=None, temperature=None):
    """Envoie un prompt à un modèle local.

    format : "json" ou un JSON schema (ex: MonModele.model_json_schema())
             -> "structured output" : Ollama force la réponse à respecter le schéma.
    """
    payload = {"model": model or OLLAMA_SMALL_MODEL, "prompt": prompt, "stream": False}
    if format is not None:
        payload["format"] = format
    if temperature is not None:
        payload["options"] = {"temperature": temperature}
    response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=300).json()
    if "response" in response:
        return response["response"]
    raise Exception(response)


# ---------------------------
# PROMPTS STOCKÉS HORS DU CODE (step 2)
# ---------------------------
def load_prompt(name):
    """Charge prompts/<name>.yaml -> {"settings": {...}, "messages": [...]}"""
    if not re.fullmatch(r"[\w-]+", name):   # pas de "../" : on reste dans prompts/
        raise ValueError(f"Nom de prompt invalide : {name!r}")
    with open(os.path.join(PROMPTS_DIR, f"{name}.yaml"), "r") as file:
        return yaml.safe_load(file)


def render_messages(messages, **variables):
    """Remplace {variable} dans le contenu des messages. Les inconnues restent telles quelles."""
    return [
        {**m, "content": re.sub(r"{(\w+)}", lambda x: str(variables.get(x.group(1), x.group(0))), m["content"])}
        for m in messages
    ]


def prompt_openai(name, **variables):
    """Appelle OpenAI avec le prompt et les paramètres définis dans prompts/<name>.yaml."""
    prompt = load_prompt(name)
    settings = prompt.get("settings") or {}
    return _chat(render_messages(prompt["messages"], **variables), **settings)


# ---------------------------
# EMBEDDINGS
# ---------------------------
def embeddings_openai(text, model=None):
    response = _openai_client().embeddings.create(model=model or OPENAI_EMBEDDING_MODEL, input=[text])
    return response.data[0].embedding
