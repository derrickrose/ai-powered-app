# STEP 3 BIS — Breed Advisor avec CLAUDE
# Seulement la partie 3.1 (recommandation par LLM), avec Claude au lieu d'OpenAI.
# La partie 3.2 (/breed_score) n'a PAS de version Claude : c'est du CODE simple,
# il n'y a pas d'IA à remplacer. C'est justement la leçon de la step 3.
# Les réponses arrivent dans `text` sous la forme "réponse1|réponse2|...".
# Sans ANTHROPIC_API_KEY, cette step est sautée.

from fastapi import APIRouter
from helpers import *
import ai_claude
router = APIRouter()

import yaml
with open('steps/step3_questions.yaml', 'r') as file:
    questions = [question['question'] for category in yaml.safe_load(file)['questions'] for question in category['questions']]

@ai_claude.needs_claude
def test_which_dog_breed_should_i_choose_chihuahua_claude():
    return check('/claude/which_dog_breed_should_i_choose', 
             ['Not very active', 'No yard', 'No pets', 'Not comfortable with training', '0 to 4 hours', 'Rarely', 'Yes, specific breed', 'Chihuahua', 'Companion', 'Not for protection', 'Not very', 'Small budget', 'Sure', 'Cannot make necessary adjustments', 'No, not good with other animals'],
             'Spaniel|Basset|Poodle|Chihuahua')

@ai_claude.needs_claude
def test_which_dog_breed_should_i_choose_jack_russell_terrier_claude():
    return check('/claude/which_dog_breed_should_i_choose', 
             ['Very active', 'Large yard', 'No pets', 'Very comfortable with training', 'More than 10 hours', 'Always', 'Yes, specific breed', 'Jack Russell Terrier', 'Companion', 'For active play', 'Very', 'Moderate budget', 'Sure', 'Can make necessary adjustments', 'Yes, good with other animals'],
             'Labrador|Spaniel|Jack Russel|Terrier|Bulldog')


@router.get("/claude/which_dog_breed_should_i_choose")
async def which_dog_breed_should_i_choose_claude(text: str):
    return "Write your code here"
