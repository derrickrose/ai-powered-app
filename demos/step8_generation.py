# STEP 8 — Génération structurée (démo, pas de test automatique)
# But : obtenir d'un LLM une sortie au FORMAT GARANTI (JSON qui respecte un schéma),
#       pour pouvoir l'utiliser dans le code. Cas d'usage : "fausse activité" dans l'app.
#
# Avant : librairie Outlines + TinyLlama chargé dans le process (API Outlines changée depuis).
# Maintenant : "structured outputs" natif d'Ollama (on lui passe le JSON schema Pydantic),
#              puis Pydantic VALIDE le résultat. (OpenAI propose la même chose : response_format.)
#
# Lancer : docker compose run --rm --service-ports generation  -> http://localhost:8501

# Les démos sont dans demos/ : on se place à la racine du projet pour
# importer helpers/ai/steps et ouvrir steps/*.yaml, output/...
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from enum import Enum

import streamlit as st
from pydantic import BaseModel, Field, ValidationError

import ai


class Name(str, Enum):
    alice = 'Alice'
    bob = 'Bob'
    claire = 'Claire'


class Comment(BaseModel):
    name: Name
    comment: str = Field(min_length=10, max_length=200)


def generate_comment(topic):
    raw = ai.ollama(
        f"Generate a short social media comment about {topic}. Answer in JSON.",
        format=Comment.model_json_schema(),   # le modèle est forcé de suivre ce schéma
        temperature=0.8,
    )
    # Le schéma garantit la FORME ; Pydantic vérifie aussi les contraintes (longueur...)
    return Comment.model_validate_json(raw)


def main():
    st.title('Comment generator (structured output)')
    st.caption(f'Modèle local : {ai.OLLAMA_SMALL_MODEL}')
    themes = ['Cats instincts', 'Cats behavior', 'Cats health', 'Cats nutrition', 'Cats training',
              'Dogs instincts', 'Dogs behavior', 'Dogs health', 'Dogs nutrition', 'Dogs training']
    selected_theme = st.selectbox('Select a theme', themes)
    if st.button('Generate'):
        try:
            st.json(generate_comment(selected_theme).model_dump(mode='json'))
        except ValidationError as e:
            st.error(f'Le modèle a produit une sortie invalide (ça arrive avec les petits modèles) :\n{e}')


if __name__ == '__main__':
    main()
