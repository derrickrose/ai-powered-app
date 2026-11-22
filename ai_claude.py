"""Accès à Claude (Anthropic) — l'équivalent de ai.py pour les steps *_bis.

- claude()        : envoie un prompt simple à Claude.
- prompt_claude() : appelle Claude avec un prompt stocké dans prompts/<nom>.yaml (step 2 bis).
- parse()         : sortie structurée, validée par un modèle Pydantic (step 8 bis).
- create()        : appel bas niveau (messages, system, tools...) utilisé par la démo step 5 bis.

Différences importantes avec OpenAI (voir resources/ANTHROPIC_API_KEY.md) :
- le prompt "system" est un paramètre à part, pas un message ;
- max_tokens est obligatoire ;
- pas de temperature / top_p / penalties sur les modèles actuels : on règle l'EFFORT
  (low / medium / high / xhigh / max), c'est-à-dire combien le modèle réfléchit.

Configuration dans .env : ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ANTHROPIC_EFFORT.
"""
import functools
import os

import anthropic

import ai  # réutilise load_prompt / render_messages (lecture des fichiers YAML)

ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5-5")
ANTHROPIC_EFFORT = os.environ.get("ANTHROPIC_EFFORT", "low")  # tâches simples du workshop
DEFAULT_MAX_TOKENS = 16000  # la réflexion du modèle compte aussi dans max_tokens : ne pas mettre trop bas

# Modèles qui acceptent le "repli" côté serveur : si le modèle refuse une demande
# (filtres de sécurité), l'API relance automatiquement la même demande sur un autre modèle.
_FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5", "claude-fable-5-2", "claude-fable-5-1"}

_client = None


def has_key():
    return os.environ.get("ANTHROPIC_API_KEY") not in (None, "", "UNSET")


def _anthropic_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY
    return _client


def _check_refusal(response):
    if response.stop_reason == "refusal":
        details = getattr(response, "stop_details", None)
        raise RuntimeError(f"Claude a refusé la demande ({getattr(details, 'category', None)})")


def text_of(response):
    """Concatène les blocs de texte de la réponse (ignore les blocs de réflexion, d'outils...)."""
    _check_refusal(response)
    return "".join(block.text for block in response.content if block.type == "text")


def create(messages, system=None, model=None, effort=None, max_tokens=DEFAULT_MAX_TOKENS, **extra):
    """Appel bas niveau à l'API Messages. extra : tools=..., etc."""
    model = model or ANTHROPIC_MODEL
    params = dict(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        output_config={"effort": effort or ANTHROPIC_EFFORT},
        **extra,
    )
    if system:
        params["system"] = system
    if model in _FALLBACK_MODELS:
        return _anthropic_client().beta.messages.create(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **params
        )
    return _anthropic_client().messages.create(**params)


def claude(prompt, system=None, model=None, effort=None, max_tokens=DEFAULT_MAX_TOKENS):
    """Envoie un prompt simple à Claude et renvoie le texte de la réponse."""
    return text_of(create([{"role": "user", "content": prompt}],
                          system=system, model=model, effort=effort, max_tokens=max_tokens))


def prompt_claude(name, **variables):
    """Appelle Claude avec prompts/<name>.yaml.

    settings acceptés : model, max_tokens, effort.
    Les messages "system" du fichier sont envoyés dans le paramètre system (règle de l'API Claude).
    """
    prompt = ai.load_prompt(name)
    settings = prompt.get("settings") or {}
    messages = ai.render_messages(prompt["messages"], **variables)
    system = "\n".join(m["content"] for m in messages if m["role"] == "system") or None
    conversation = [m for m in messages if m["role"] != "system"]
    return text_of(create(conversation, system=system, model=settings.get("model"),
                          effort=settings.get("effort"),
                          max_tokens=settings.get("max_tokens", DEFAULT_MAX_TOKENS)))


def parse(prompt, output_format, model=None, effort=None, max_tokens=DEFAULT_MAX_TOKENS):
    """Sortie structurée : Claude répond selon le schéma du modèle Pydantic, le SDK valide."""
    response = _anthropic_client().messages.parse(
        model=model or ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        output_format=output_format,
        output_config={"effort": effort or ANTHROPIC_EFFORT},
    )
    _check_refusal(response)
    return response.parsed_output


def judge(question):
    """Juge pour helpers.check_ai : les steps *_bis n'ont besoin que de la clé Anthropic."""
    return claude(question)


def needs_claude(test):
    """Décorateur de test : sans ANTHROPIC_API_KEY, la step Claude est sautée (pas bloquante)."""
    @functools.wraps(test)
    def wrapper():
        from helpers import ok, yellow
        if not has_key():
            return ok(yellow("ANTHROPIC_API_KEY absente : step Claude (_bis) ignorée"))
        return test()
    return wrapper
