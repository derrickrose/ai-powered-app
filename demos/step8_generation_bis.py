# STEP 8 BIS — Génération structurée avec CLAUDE (démo, pas de test automatique)
# Même démo que step8_generation.py (Ollama local), mais avec Claude dans le cloud.
# Outil : ai_claude.parse(prompt, MonModelePydantic)
#   -> Claude répond selon le JSON schema du modèle, le SDK Anthropic valide et
#      renvoie directement un objet Pydantic.
#
# Lancer : docker compose run --rm --service-ports generation-bis  -> http://localhost:8501

# Les démos sont dans demos/ : on se place à la racine du projet pour
# importer helpers/ai/steps et ouvrir steps/*.yaml, output/...
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from enum import Enum

import streamlit as st
from pydantic import BaseModel, Field, ValidationError

import ai_claude


class Name(str, Enum):
    alice = 'Alice'
    bob = 'Bob'
    claire = 'Claire'


class Comment(BaseModel):
    name: Name
    comment: str = Field(min_length=10, max_length=200)


def generate_comment(topic):
    return ai_claude.parse(f"Generate a short social media comment about {topic}.", Comment)


def main():
    st.title('Comment generator (Claude, structured output)')
    st.caption(f'Modèle : {ai_claude.ANTHROPIC_MODEL}')
    themes = ['Cats instincts', 'Cats behavior', 'Cats health', 'Cats nutrition', 'Cats training',
              'Dogs instincts', 'Dogs behavior', 'Dogs health', 'Dogs nutrition', 'Dogs training']
    selected_theme = st.selectbox('Select a theme', themes)
    if st.button('Generate'):
        try:
            st.json(generate_comment(selected_theme).model_dump(mode='json'))
        except ValidationError as e:
            st.error(f'Sortie invalide :\n{e}')


if __name__ == '__main__':
    main()
