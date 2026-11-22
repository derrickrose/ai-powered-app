# STEP 1 BIS — Prompting LLM avec CLAUDE (Anthropic)
# Même exercice que step1_prompting.py, mais avec Claude au lieu d'OpenAI.
# Outil : ai_claude.claude(prompt, system=...)   — routes préfixées par /claude/
# But en plus : comparer deux fournisseurs de LLM sur les mêmes tâches (qualité, style, coût).
# Différences à connaître : le prompt "system" est un paramètre séparé ; pas de temperature,
# on règle l'effort (low/medium/high) — voir resources/ANTHROPIC_API_KEY.md.
# Sans ANTHROPIC_API_KEY, cette step est sautée.

from fastapi import APIRouter
from helpers import *
import ai_claude
router = APIRouter()

@ai_claude.needs_claude
def test_summarize():
    return check_ai('/claude/summarize', 
             """Ducks are fascinating creatures known for their versatile habitats, ranging from freshwater lakes to coastal shorelines. These birds are admired for their vibrant plumage and distinctive quacking sounds. Ducks play a crucial role in their ecosystems by helping control insect and aquatic plant populations. They're also migratory, often traveling long distances between breeding and wintering grounds. Ducks' waterproof feathers and unique swimming ability make them adept at surviving in various environments. Their diet includes aquatic plants, small fish, and insects, showcasing their adaptability. In many cultures, ducks are symbols of freedom and grace, embodying the serene beauty of nature.""",
             """Is "{response}" is a valid summarization of this text: {text}.  Answer yes or no. Just single word""", 
             '^yes', judge=ai_claude.judge)

@router.get("/claude/summarize")
async def summarize_claude(text: str):
    return 'Write your code here'




@ai_claude.needs_claude
def test_sentiment():
    return all_ok(check('/claude/sentiment', 'Kinda ok.', 'neutral'),
                  check('/claude/sentiment', 'I\'m so glad. That awesome', 'positive'),
                  check('/claude/sentiment', "Feeling terrible. It's awful", 'negative'))

@router.get("/claude/sentiment")
async def sentiment_claude(text: str):
    return 'Write your code here'




@ai_claude.needs_claude
def test_generate_code():
    return check('/claude/generate_code', 'Write hello world in python', 'print(.*hello.*world.*)')

@router.get("/claude/generate_code")
async def generate_code_claude(text: str):
    return 'Write your code here'




@ai_claude.needs_claude
def test_keypoints():
    return check_ai('/claude/keypoints', 
             "Artificial intelligence is a branch of computer science that aims to create machines that can perform tasks that typically require human intelligence. This includes tasks like problem-solving, recognizing speech, translating languages, and more. AI systems are powered by algorithms, use deep learning and machine learning to process data, and can improve their performance over time as they acquire more data.",
             "Do the key points extracted from the text: {text} match the following summary: {response}? Answer yes or no. Just single word", 
             '^yes', judge=ai_claude.judge)

@router.get("/claude/keypoints")
async def keypoints_claude(text: str):
    return 'Write your code here'




@ai_claude.needs_claude
def test_questions():
    return check_ai('/claude/questions', 
             "What are the implications of quantum computing on current encryption methods? With the potential to process information at significantly faster rates, quantum computers could theoretically break many of the cryptographic algorithms that keep our digital communications secure. As a result, there is a growing need for quantum-resistant encryption methods that can withstand the processing power of quantum technology.",
             "Do the questions extracted from the text: {text} match the following: {response}? Answer yes or no. Just single word", 
             '^yes', judge=ai_claude.judge)

@router.get("/claude/questions")
async def questions_claude(text: str):
    return 'Write your code here'