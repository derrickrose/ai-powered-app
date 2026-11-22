# STEP 0 — Configuration
# But : vérifier que les clés et les modèles locaux sont prêts. Rien à coder.
# Les valeurs viennent de .env (voir .env.example), jamais en dur dans le code.

from helpers import *

import os
os.environ.setdefault("OPENAI_API_KEY", "UNSET")
os.environ.setdefault("HUGGING_FACE_API_KEY", "UNSET")
os.environ.setdefault("ANTHROPIC_API_KEY", "UNSET")


def test_openai_keys():
    if os.environ.get("OPENAI_API_KEY") in ("UNSET", ""):
        return fail("OPENAI_API_KEY n'est pas définie. Copie .env.example en .env et remplis-la.")
    return ok(f"OPENAI_API_KEY est définie (modèle : {ai.OPENAI_MODEL})")


def test_anthropic_key():
    # Optionnel : seulement pour les steps *_bis (Claude). Sans clé, elles sont sautées.
    if os.environ.get("ANTHROPIC_API_KEY") in ("UNSET", ""):
        return ok(yellow("ANTHROPIC_API_KEY non définie (optionnel : steps *_bis avec Claude)."))
    import ai_claude
    return ok(f"ANTHROPIC_API_KEY est définie (modèle : {ai_claude.ANTHROPIC_MODEL})")


def test_hugging_face_key():
    # Optionnel : les modèles publics utilisés dans le workshop fonctionnent sans token.
    if os.environ.get("HUGGING_FACE_API_KEY") in ("UNSET", ""):
        return ok(yellow("HUGGING_FACE_API_KEY non définie (optionnel). https://huggingface.co/settings/tokens"))
    return ok("HUGGING_FACE_API_KEY est définie")


def test_ollama_models():
    for model in [ai.OLLAMA_SMALL_MODEL, ai.OLLAMA_MEDIUM_MODEL]:
        try:
            response = ai.ollama(prompt='Say "test"', model=model, temperature=0)
            if "test" not in response.lower():
                return fail(f"Le modèle Ollama {model} ne répond pas correctement : {response}")
        except Exception as e:
            return fail(f"Le modèle Ollama {model} est en erreur : {e}",
                        "\nLance : docker compose up ollama-pull")
    return ok(f"Modèles Ollama {ai.OLLAMA_SMALL_MODEL}, {ai.OLLAMA_MEDIUM_MODEL} OK.")
