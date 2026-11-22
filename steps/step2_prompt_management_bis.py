# STEP 2 BIS — Gestion des prompts hors du code, avec CLAUDE
# Même idée que step2_prompt_management.py : un fichier YAML par prompt dans prompts/.
# Ce que tu apprends en plus : les paramètres ne sont PAS les mêmes d'un fournisseur à l'autre.
#   OpenAI : temperature, top_p, presence/frequency_penalty
#   Claude : effort (low/medium/high/xhigh/max), max_tokens obligatoire, system à part
#
# À FAIRE :
#   1. Créer prompts/claude_test.yaml      (voir prompts/claude_example.yaml et test_claude_prompt_file_settings)
#   2. Créer prompts/claude_variables.yaml (un prompt qui utilise la variable {value})
# Le code des endpoints est déjà fourni. Sans ANTHROPIC_API_KEY, cette step est sautée.

from fastapi import APIRouter
from helpers import *
import ai
import ai_claude
router = APIRouter()


@ai_claude.needs_claude
def test_claude_prompt_file_settings():
    try:
        prompt = ai.load_prompt("claude_test")
    except FileNotFoundError:
        return fail("Crée le fichier prompts/claude_test.yaml (modèle : prompts/claude_example.yaml)")

    settings = prompt.get('settings') or {}
    error_messages = []
    if not str(settings.get('model', '')).startswith('claude-'):
        error_messages.append("settings.model doit être un modèle Claude (ex: claude-opus-5-5).")
    if settings.get('effort') != 'low':
        error_messages.append(f"settings.effort doit valoir low (trouvé : {settings.get('effort')}).")
    if not isinstance(settings.get('max_tokens'), int) or settings['max_tokens'] < 256:
        error_messages.append("settings.max_tokens doit être un entier >= 256 (il inclut la réflexion du modèle).")
    forbidden = [k for k in ('temperature', 'top_p', 'presence_penalty', 'frequency_penalty') if k in settings]
    if forbidden:
        error_messages.append(f"Retire {forbidden} : ces paramètres n'existent pas (ou sont refusés) chez Claude.")

    expected_messages = [
        {'role': 'system', 'content': 'Do not describe your answers. Answer in json.'},
        {'role': 'user', 'content': 'Answer "test".'}
    ]
    if prompt.get('messages') != expected_messages:
        error_messages.append(f"messages attendus : {expected_messages}, trouvés : {prompt.get('messages')}")

    if error_messages:
        for message in error_messages:
            fail(message)
        return fail("Corrige prompts/claude_test.yaml")

    return ok("prompts/claude_test.yaml contient les bons paramètres et messages.")


@ai_claude.needs_claude
def test_claude_prompt_test():
    return check_ai('/claude/prompt_test', '', 'Does {response} looks like {"answer":"test"}. Answer yes or no', 'yes',
                    judge=ai_claude.judge)


@router.get("/claude/prompt_test")
async def claude_prompt_test():
    return ai_claude.prompt_claude('claude_test')


@ai_claude.needs_claude
def test_claude_prompt_variables():
    return check('/claude/prompt_variables?value=foobar', '', 'foobar')


@router.get("/claude/prompt_variables")
async def claude_prompt_variables(value='unset'):
    return ai_claude.prompt_claude('claude_variables', value=value)
