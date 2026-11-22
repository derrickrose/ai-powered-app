# STEP 2 — Gestion des prompts hors du code
# But : séparer le prompt (texte + paramètres) du code applicatif, et le versionner.
# Avant : le service en ligne Pezzo (projet devenu inactif).
# Maintenant : un fichier YAML par prompt dans prompts/, versionné avec git.
# En production : Langfuse, PromptLayer, Braintrust... (voir README).
#
# À FAIRE :
#   1. Créer prompts/test.yaml      (voir prompts/example.yaml et les attentes de test_prompt_file_settings)
#   2. Créer prompts/variables.yaml (un prompt qui utilise la variable {value})
# Le code des endpoints est déjà fourni.

from fastapi import APIRouter
from helpers import *
import ai
router = APIRouter()


def test_prompt_file_settings():
    try:
        prompt = ai.load_prompt("test")
    except FileNotFoundError:
        return fail("Crée le fichier prompts/test.yaml (modèle : prompts/example.yaml)")

    settings = prompt.get('settings') or {}
    expected_settings = {'top_p': 0.8, 'max_tokens': 10, 'temperature': 0,
                         'presence_penalty': 0.2, 'frequency_penalty': 1}
    error_messages = []
    if not settings.get('model'):
        error_messages.append("settings.model doit être défini (ex: gpt-4.1-mini).")
    for key, value in expected_settings.items():
        if settings.get(key) != value:
            error_messages.append(f"settings.{key} doit valoir {value} (trouvé : {settings.get(key)}).")

    expected_messages = [
        {'role': 'system', 'content': 'Do not describe your answers. Answer in json.'},
        {'role': 'user', 'content': 'Answer "test".'}
    ]
    if prompt.get('messages') != expected_messages:
        error_messages.append(f"messages attendus : {expected_messages}, trouvés : {prompt.get('messages')}")

    if error_messages:
        for message in error_messages:
            fail(message)
        return fail("Corrige prompts/test.yaml")

    return ok("prompts/test.yaml contient les bons paramètres et messages.")


def test_prompt_test():
    return check_ai('/prompt_test', '', 'Does {response} looks like {"answer":"test"}. Answer yes or no', 'yes')


@router.get("/prompt_test")
async def prompt_test():
    return ai.prompt_openai('test')


def test_prompt_variables():
    return check('/prompt_variables?value=foobar', '', 'foobar')


@router.get("/prompt_variables")
async def prompt_variables(value='unset'):
    return ai.prompt_openai('variables', value=value)
