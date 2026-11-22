# Les démos sont dans demos/ : on se place à la racine du projet pour
# importer helpers/ai/steps et ouvrir steps/*.yaml, output/...
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import gradio as gr
import yaml
from helpers import * 

import requests

# Interface du step 3 : affiche le questionnaire et appelle les 2 endpoints.

def breed_advisor(*answers):
    return requests.get(f"{SERVER_URL}/which_dog_breed_should_i_choose", params={"text": join('|', map(str, answers))}).text

def breed_score(*answers):
    return requests.get(f"{SERVER_URL}/breed_score", params={"text": join('|', map(str, answers))}).text

# Load questions from the YAML file
with open('steps/step3_questions.yaml', 'r') as file:
    questions_data = yaml.safe_load(file)

# Extract questions and options
questions = []
for category in questions_data['questions']:
    for question in category['questions']:
        q_text = question['question']
        q_answers = question['answers']
        questions.append({'question': q_text, 'options': q_answers})

# # Create Gradio interface
def setup_gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown("### Breed Advisor Questionnaire")
        inputs = []
        for q in questions:
            inputs.append(gr.Radio(q['options'], label=q['question']))
        gr.Button("Get advice").click(breed_advisor, inputs, gr.Textbox(label="Breed Advice"))
        gr.Button("Get score").click(breed_score, inputs, gr.Textbox(label="Breed Score"))
    return demo

app = setup_gradio_interface()

# share=True créerait un lien public via les serveurs de Gradio : désactivé par défaut
app.launch(server_name="0.0.0.0", server_port=7860)