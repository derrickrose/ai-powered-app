# STEP 6 — Reconnaissance de race par photo
# But : utiliser un modèle SPÉCIALISÉ de classification d'images (Hugging Face)
#       plutôt qu'un LLM : rapide, gratuit, local, et il renvoie des scores.
# Outil : transformers.pipeline("image-classification", model=...)
# L'endpoint doit renvoyer la liste [{"label": ..., "score": ...}, ...] triée par score.

from fastapi import APIRouter
import requests
from helpers import *
import ai
from fastapi import UploadFile, File

router = APIRouter()


def normalize_label(label):
    # Les modèles nomment les classes différemment :
    # "standard poodle", "Scotch terrier, Scottish terrier, Scottie", "standard_poodle"...
    # -> on garde le 1er nom, en minuscules, avec des "_" : "standard_poodle", "scotch_terrier"
    return str(label).split(',')[0].strip().lower().replace(' ', '_')


def recognize(image_path, expected_breed):
    with open(image_path, 'rb') as file:
        response = requests.post(f"{SERVER_URL}/recognize_dog_breed", files={'file': (image_path, file, 'image/jpeg')}, timeout=300)
        if response.status_code == 200:
            data = response.json()
            try:
                highest_matching_breed = data[0]['label']
            except (KeyError, IndexError, TypeError):
                return fail(f"{image_path}. Unexpected response: {data}")
            if normalize_label(highest_matching_breed) == expected_breed:
                return ok(highest_matching_breed)

            return fail(f"{image_path}. Expected breed: {expected_breed}, Detected breeds: {', '.join(pluck('label', data))}")
        else:
            return fail(f"{image_path}. Status code: {response.status_code}")

def test_recognize_poodle():
    return recognize('./images/poodle.jpeg', 'standard_poodle')

def test_recognize_terrier():
    return recognize('./images/scottish-terrier.jpeg', 'scotch_terrier')



@router.post("/recognize_dog_breed")
async def recognize_dog_breed(file: UploadFile = File(...)):
    content = await file.read()
    return "Write your code here"
