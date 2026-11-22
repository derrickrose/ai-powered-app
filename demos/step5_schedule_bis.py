# STEP 5 BIS (bonus) — Planning de promenades avec l'outil ("tool use") de CLAUDE
# Même démo que step5_schedule.py, avec Claude au lieu d'OpenAI.
# But : voir la BOUCLE d'un agent : Claude demande un outil -> le code l'exécute ->
#       on lui renvoie le résultat -> il continue, jusqu'à ce qu'il ait fini.
# Différences avec OpenAI : l'outil se décrit avec "input_schema" ; Claude renvoie des
# blocs "tool_use" et on répond avec des blocs "tool_result" dans un message "user".
# À FAIRE : écrire le prompt (variable prompt) pour obtenir un planning heure par heure.
#
# Lancer : docker compose run --rm --service-ports schedule-bis  -> http://localhost:8501

# Les démos sont dans demos/ : on se place à la racine du projet pour
# importer helpers/ai/steps et ouvrir steps/*.yaml, output/...
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import random

import steps.step0_setup
import ai_claude


def get_current_weather(location, time, unit="celsius"):
    # En vrai : une API météo (ex : Open-Meteo). Ici, une valeur au hasard.
    print(f'get_current_weather called ({location}, {time}, {unit})')
    return random.choice(["sunny", "rainy", "cloudy", "snowy"])


TOOLS = [
    {
        "name": "get_current_weather",
        "description": "Get the weather in a given location at a given time of today.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The city, e.g. New York"},
                "time": {"type": "string", "description": "Time, like: 12:00 or 4:00PM"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location", "time"],
        },
    }
]
AVAILABLE_FUNCTIONS = {"get_current_weather": get_current_weather}


def run_conversation(location, max_turns=10):
    # TODO : écrire un prompt qui demande un planning de promenade heure par heure (10:00 -> 20:00)
    # à `location`, en choisissant un parc s'il fait beau et un lieu couvert sinon,
    # et en vérifiant la météo de CHAQUE heure avec l'outil.
    prompt = f"""

    """
    messages = [{"role": "user", "content": prompt}]

    for _ in range(max_turns):
        response = ai_claude.create(messages, tools=TOOLS)
        if response.stop_reason != "tool_use":
            return ai_claude.text_of(response)          # Claude a fini

        # 1. on garde la réponse de Claude (avec ses demandes d'outils) dans l'historique
        messages.append({"role": "assistant", "content": response.content})
        # 2. on exécute chaque outil demandé, et on renvoie TOUS les résultats d'un coup
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                function = AVAILABLE_FUNCTIONS.get(block.name)
                if function is None:
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                         "content": f"Unknown tool {block.name}", "is_error": True})
                    continue
                result = function(**block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "user", "content": tool_results})

    return "Arrêt : trop de tours (max_turns)."


if __name__ == '__main__':
    import streamlit as st

    st.title('Dog Walk Scheduler (Claude)')
    st.caption(f'Modèle : {ai_claude.ANTHROPIC_MODEL}')
    location = st.text_input('Enter location', 'New York')
    if st.button('Run Conversation'):
        st.write('Conversation result:', run_conversation(location))
