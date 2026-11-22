# STEP 9 BIS — Modération des commentaires avec CLAUDE
# Même exercice que step9_filter.py (mêmes commentaires, même objectif 10/10), avec Claude.
# Ce que tu apprends en plus : un prompt réglé pour un modèle ne donne pas forcément
# le même résultat sur un autre -> il faut re-tester quand on change de fournisseur.
# Techniques : system prompt clair, exemples few-shot, nettoyage de la réponse.
# (Pas de temperature chez Claude : pour une classification, effort "low" suffit.)
# Sans ANTHROPIC_API_KEY, cette step est sautée.

from fastapi import APIRouter
from helpers import *
import ai_claude
from steps.step9_filter import run_cat_mafia_test
router = APIRouter()


@ai_claude.needs_claude
def test_claude_classify_comment_positive():
    return check('/claude/classify_comment', 'You are terrible person who hates dogs.', 'abusive')


@ai_claude.needs_claude
def test_claude_classify_comment_negative():
    return check('/claude/classify_comment', 'I love dogs.', 'ok')


@router.get("/claude/classify_comment")
def classify_comment_abusive_claude(text: str):
    return 'Write your code here'


@ai_claude.needs_claude
def test_claude_filter_cat_mafia():
    return run_cat_mafia_test('/claude/filter_cat_mafia')


@router.get('/claude/filter_cat_mafia')
def filter_cats_claude(text: str):
    #TODO: try to improve accuracy
    return ai_claude.claude(
        f"This is a message:\n    {text}",
        system="""We need to filter messages from cats. Return one of "cat", "ok", 'probably cat', 'probably ok'.""",
    )
