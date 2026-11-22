"""Outils de test du workshop (ce n'est pas de l'IA, c'est le "correcteur").

- check()    : appelle un endpoint et vérifie la réponse avec une regex (test classique, déterministe).
- check_ai() : appelle un endpoint puis demande à un LLM si la réponse est correcte
               (OpenAI par défaut, ou un autre juge : check_ai(..., judge=ai_claude.judge))
               ("LLM-as-a-judge" : utile quand il n'y a pas UNE bonne réponse, ex: un résumé).
- all_ok()   : combine plusieurs résultats de check.
"""
import os
import re
import importlib

import requests
from ramda import *

import ai

SERVER_URL = os.environ.get("SERVER_URL", "http://server:8000")


def fail(message, explanation=''):
    print(f"\033[91mFAIL \033[0m{message} {explanation}\n")
    return 'FAIL'


def ok(message):
    print(f"\033[92mOK\033[0m {message}\n")
    return "OK"


def all_ok(*results):
    """'FAIL' si au moins un résultat a échoué. ('FAIL' est une chaîne non vide : `a and b` ne marche pas.)"""
    return 'FAIL' if 'FAIL' in results else 'OK'


def yellow(message):
    return f"\033[93m{message}\t\033[0m"


def green(message):
    return f"\033[92m{message}\t\033[0m"


def red(message):
    return f"\033[91m{message}\t\033[0m"


def check_server_response():
    try:
        response = requests.get(SERVER_URL, timeout=10)
        if not response.status_code == 200:
            fail("Server responded with unexpected status code", str(response.status_code))
    except requests.exceptions.RequestException as e:
        fail("Server request failed", str(e))


def GET(endpoint, query):
    """GET sur le serveur avec ?text=query. Une liste est envoyée sous la forme 'a|b|c'."""
    if isinstance(query, (list, tuple)):
        query = '|'.join(map(str, query))
    try:
        response = requests.get(f'{SERVER_URL}{endpoint}', params={'text': query}, timeout=300)
        if response.ok:
            return response.text, response.ok
        return f'Failed response: {endpoint} ({response.status_code})', False
    except requests.exceptions.RequestException:
        return f'Failed response: {endpoint}', False


def match_regex(text, regex):
    pattern = re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return re.search(pattern, text)


def check_ai(endpoint, text, question, regex, judge=None):
    """judge : fonction question -> réponse. Par défaut OpenAI ; les steps *_bis passent Claude."""
    response, ok_ = GET(endpoint, text)

    question = replace('{text}', '\n' + text + '\n', replace('{response}', '\n' + response + '\n', question))
    aianswer = judge(question) if judge else ai.openai(question, temperature=0)

    ok_ = bool(ok_ and match_regex(aianswer, regex))
    message = "\n\t\t".join([
        endpoint,
        f"{yellow('QUERY')}{text}",
        f"{yellow('ANSWER')}{response}",
        f"{yellow('AICHECK QUERY')}{question}\n",
        f"{yellow('AICHECK')}{aianswer}",
        f"{green('OK')}/{regex}/" if ok_ else f"{red('FAIL')}/{regex}/"
    ])
    return ok(message) if ok_ else fail(message)


def check(endpoint, text, regex):
    response, ok_ = GET(endpoint, text)

    ok_ = bool(ok_ and match_regex(response, regex))

    message = "\n\t\t".join([
        endpoint,
        f"{yellow('QUERY')}{text}",
        f"{yellow('ANSWER')}{response}",
        f"{green('OK')}/{regex}/" if ok_ else f"{red('FAIL')}/{regex}/"
    ])
    return ok(message) if ok_ else fail(message)


def find_steps():
    steps_path = os.path.join(os.path.dirname(__file__), 'steps')
    for module_name in sorted(os.listdir(steps_path)):
        if module_name.endswith('.py') and module_name != '__init__.py':
            module_name = module_name[:-3]  # Remove .py extension
            module = importlib.import_module(f'steps.{module_name}')
            yield module, module_name
