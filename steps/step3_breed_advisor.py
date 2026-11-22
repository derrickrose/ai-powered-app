# STEP 3 — Breed Advisor
# But : comparer DEUX façons de recommander une race à partir d'un questionnaire.
#   3.1 /which_dog_breed_should_i_choose -> avec un LLM (flexible, mais variable et payant)
#   3.2 /breed_score                     -> avec du CODE simple (compter les réponses qui
#                                           correspondent dans step3_breeds.yaml) :
#                                           exact, gratuit, testable. Ici, pas besoin d'IA !
# Les réponses arrivent dans `text` sous la forme "réponse1|réponse2|...".

from fastapi import APIRouter
from helpers import *
import ai
router = APIRouter()

import yaml
with open('steps/step3_questions.yaml', 'r') as file:
    questions = [question['question'] for category in yaml.safe_load(file)['questions'] for question in category['questions']]
with open('steps/step3_breeds.yaml', 'r') as file:
    breeds_data = yaml.safe_load(file)

def test_which_dog_breed_should_i_choose_chihuahua():
    return check('/which_dog_breed_should_i_choose', 
             ['Not very active', 'No yard', 'No pets', 'Not comfortable with training', '0 to 4 hours', 'Rarely', 'Yes, specific breed', 'Chihuahua', 'Companion', 'Not for protection', 'Not very', 'Small budget', 'Sure', 'Cannot make necessary adjustments', 'No, not good with other animals'],
             'Spaniel|Basset|Poodle|Chihuahua')

def test_which_dog_breed_should_i_choose_jack_russell_terrier():
    return check('/which_dog_breed_should_i_choose', 
             ['Very active', 'Large yard', 'No pets', 'Very comfortable with training', 'More than 10 hours', 'Always', 'Yes, specific breed', 'Jack Russell Terrier', 'Companion', 'For active play', 'Very', 'Moderate budget', 'Sure', 'Can make necessary adjustments', 'Yes, good with other animals'],
             'Labrador|Spaniel|Jack Russel|Terrier|Bulldog')


@router.get("/which_dog_breed_should_i_choose")
async def which_dog_breed_should_i_choose(text: str):
    return "Write your code here"


def test_breed_score_consult():
    import json

    test_input = 'Very active|Prefer staying indoors|Apartment|Small yard|Yes, cats|Somewhat comfortable|4 to 8 hours|Occasionally|Not sure|Yes, specific energy level|No, open to suggestions|Exercise partner|Protection|Somewhat|No specific budget, but have financial limits|Unsure|Can make necessary adjustments|Yes, good with other animals'
    expected_output = {'whippet': 1, 'greyhound': 3, 'labrador_retriever': 18, 'french_bulldog': 12, 'german_shepherd': 16, 'beagle': 11, 'golden_retriever': 17, 'poodle': 7, 'boxer': 10}
    response, ok_ = GET("/breed_score", test_input)
    if not ok_:
        return fail("Breed score consult test failed.", "Endpoint /breed_score did not return a successful response.")
    try:
        result = json.loads(response)
    except ValueError:
        return fail("Breed score consult test failed.", f"Response is not JSON: {response}")
    if result == expected_output:
        return ok("Breed score consult test passed.")
    return fail("Breed score consult test failed.", f"Expected {expected_output}, but got {result}")


@router.get("/breed_score")
def score_breeds(text: str):
    return "Write your code here"
