# STEP 9/10 — Human in the loop : un humain classe les commentaires à la main ;
# ces exemples servent ensuite d'exemples "few-shot" pour améliorer le prompt du step 9.

# Les démos sont dans demos/ : on se place à la racine du projet pour
# importer helpers/ai/steps et ouvrir steps/*.yaml, output/...
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import streamlit as st
import yaml
from ramda import *

with open('./steps/step9_comments.yaml', 'r') as file:
    comments = yaml.safe_load(file)['comments']

cat_comments = []
ok_comments = []

st.title('Comment Classification')

for comment in comments:
    st.write(f'{comment}')
    if st.radio('Classify Comment', ['ok', 'cat mafia'], key=comment) == 'cat mafia':
        cat_comments.append(comment)
    else:
        ok_comments.append(comment)

st.title('Examples of "cat" comments:')
st.write(join('\n\n', cat_comments))

st.title('Examples of "ok" comments:')
st.write(join('\n\n', ok_comments))
