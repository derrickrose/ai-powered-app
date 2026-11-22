# Python — le minimum pour le workshop

Pas besoin d'être expert. Voici ce qui revient dans les exercices.

## Chaînes de caractères et f-strings

```python
name = "Rex"
prompt = f"Write a short poem about a dog named {name}."   # f-string : {variable} est remplacé
answer = "  Positive.\n"
clean = answer.strip().lower().rstrip(".")                  # -> "positive"  (nettoyer une réponse de LLM)
parts = "Very active|No yard|No pets".split("|")             # -> ["Very active", "No yard", "No pets"]
```

## Listes et dictionnaires

```python
scores = {}                          # dictionnaire vide
for breed in ["beagle", "boxer"]:
    scores[breed] = 0
scores["beagle"] += 1                # -> {"beagle": 1, "boxer": 0}

best = max(scores, key=scores.get)   # la clé avec la plus grande valeur
```

## Fonctions et endpoints FastAPI

```python
from fastapi import APIRouter
router = APIRouter()

@router.get("/hello")              # GET /hello?text=...
async def hello(text: str):
    return f"Hello {text}"         # FastAPI renvoie la valeur en JSON
```

Tester à la main : http://localhost:8000 (doc Swagger), bouton "Try it out".

## Lire un fichier YAML

```python
import yaml
with open("steps/step3_breeds.yaml") as file:
    breeds = yaml.safe_load(file)   # -> dict Python
```

## JSON

```python
import json
data = json.loads('{"answer": "test"}')   # texte -> dict
text = json.dumps({"answer": "test"})     # dict -> texte
```

## Gérer une erreur

```python
try:
    data = json.loads(llm_answer)
except ValueError:
    data = None        # le LLM n'a pas renvoyé du JSON valide
```

## Appeler l'IA dans le workshop

```python
import ai
ai.openai("Say hello", temperature=0)   # LLM cloud
ai.ollama("Say hello")                  # LLM local
```

Pour aller plus loin : https://docs.python.org/fr/3/tutorial/
