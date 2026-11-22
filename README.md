# 🐕 AI-Powered App — Workshop

Workshop pratique pour apprendre à **intégrer de l'IA dans une application** (un backend FastAPI),
et surtout à **choisir le bon outil pour chaque besoin** : un LLM, un modèle spécialisé… ou du code classique.

> 🧭 **Parcours étape par étape** (objectif, outils, installation, pourquoi, alternatives) : [docs/ETAPES.md](docs/ETAPES.md)  
> 📘 Le guide détaillé, exercice par exercice (avec solutions) : [docs/GUIDE_EXERCICES.md](docs/GUIDE_EXERCICES.md)  
> 📚 Les bases : [IA](resources/AI_TOOLS_BASICS.md) · [Docker](resources/DOCKER_BASICS.md) · [Python](resources/PYTHON_BASICS.md) · [clé OpenAI](resources/OPENAI_API_KEY.md) · [clé Claude](resources/ANTHROPIC_API_KEY.md) · [clé Hugging Face](resources/HUGGING_FACE_API_KEY.md)

---

## 1. Le but du projet

**Le scénario (pour rire)** : ton ami a pitché une startup IA pour les propriétaires de chiens.
Un investisseur veut une démo demain, mais il n'y a qu'un frontend, sans backend ni IA.
Tu dois construire : recommandation de race, planning de promenades, reconnaissance de race par photo,
"traducteur" d'aboiements, fausse activité dans l'app, modération anti "Cat Mafia".

**Le vrai but (pédagogique)** : à la fin, tu sais
1. appeler un modèle d'IA depuis une API et en tirer une réponse exploitable ;
2. choisir entre **LLM cloud** (OpenAI) et **LLM local** (Ollama) : coût, confidentialité, qualité ;
3. utiliser un **modèle spécialisé** (image, audio) quand un LLM n'est pas le bon outil ;
4. reconnaître quand **du code simple suffit** et qu'il ne faut pas d'IA ;
5. **vérifier** les réponses d'une IA (tests, LLM-as-a-judge, humain dans la boucle).

### Quel type d'IA est-ce ?

C'est une **application "AI-powered"** : un backend classique où chaque fonctionnalité fait
**un appel à un modèle** (entrée → modèle → sortie).

| Type | Présent ici ? | Où |
|---|---|---|
| **IA générative (LLM)** | ✅ | Steps 1, 2, 3.1, 5, 8, 9 |
| **ML classique / classification** | ✅ | Step 6 (image), 7 (audio) |
| **Embeddings** | ✅ (démo) | Step 4 — la brique de base du RAG |
| **Humain dans la boucle** | ✅ | Steps 9/10 |
| **Function calling** | ✅ (bonus) | Step 5 — la brique de base des agents |
| **RAG** (le modèle répond à partir de tes documents) | ❌ | → voir [Pour aller plus loin](#7-pour-aller-plus-loin) |
| **Agent IA** (le modèle choisit ses outils et boucle jusqu'au but) | ❌ | → voir [Pour aller plus loin](#7-pour-aller-plus-loin) |

---

## 2. Démarrage rapide

```bash
# 1. Clés API (une seule fois) — ne jamais committer .env
cp .env.example .env          # puis remplir OPENAI_API_KEY (et ANTHROPIC_API_KEY pour les steps _bis)

# 2. Lancer le backend + les modèles locaux (le 1er build est long : torch, transformers…)
docker compose up -d --build server ollama ollama-pull open-webui

# 3. Lancer les tests (ils s'arrêtent à la première step qui échoue)
docker compose run --rm test
rm test_cache.json            # pour tout retester depuis le début
```

| URL | Quoi |
|---|---|
| http://localhost:8000 | Doc interactive de l'API (Swagger) : tester chaque endpoint à la main |
| http://localhost:3000 | Open WebUI : discuter avec les modèles locaux |

Apps de démo (une à la fois) :
`docker compose run --rm --service-ports <breed-advisor | breed-recognition | schedule | generation | comments-review>`

### Comment se déroule le workshop

```
steps/stepN_xxx.py  =  des endpoints vides ("Write your code here")  +  des fonctions test_*()
                                     │
tests.py  → lance les steps dans l'ordre → s'arrête au 1er échec → retient les steps réussies
```

Le serveur recharge le code automatiquement : tu modifies, tu relances les tests.

### Structure du projet

```
steps/       Exercices notés (endpoints + tests) : 0, 1, 2, 3, 6, 7, 9
             + versions Claude : step1_prompting_bis, step2_prompt_management_bis,
               step3_breed_advisor_bis, step9_filter_bis
             ⚠️ chaque .py de ce dossier est importé automatiquement par le serveur et les tests
demos/       Scripts et interfaces lancés à la main (non chargés par le serveur) :
             step4_embeddings, step5_schedule(_bis), step8_generation(_bis),
             breed_advisor (step 3), breed_recognition (step 6),
             comments-human-in-the-loop (step 10), *-hello-world
prompts/     Prompts stockés hors du code (step 2)
images/      Photos de test (step 6)
docs/        ETAPES.md (parcours) et GUIDE_EXERCICES.md (exercices + solutions)
resources/   Bases : IA, Docker, Python, clés API
ai.py        Accès aux modèles (OpenAI, Ollama, prompts, embeddings)
ai_claude.py Accès à Claude (Anthropic) pour les steps _bis
helpers.py   Outils de test (check, check_ai)
server.py    Backend FastAPI
tests.py     Runner de tests
```

---

## 3. Les steps : ce que chacune t'apprend

Légende **Code ou IA ?** — ⚙️ du code suffit / 🤖 l'IA est le bon choix / ⚖️ à comparer

| Step | Fichier | Fonctionnalité | 🎯 Ce que tu apprends | Type d'IA | Code ou IA ? |
|---|---|---|---|---|---|
| 0 | `steps/step0_setup.py` | Configuration | Gérer des clés API proprement (`.env`), vérifier les modèles locaux | — | — |
| 1 | `steps/step1_prompting.py` | Résumé, sentiment, code, points clés, questions | **Prompting** : écrire un prompt qui donne une réponse exploitable par le code | LLM | 🤖 |
| 2 | `steps/step2_prompt_management.py` | Prompts dans `prompts/*.yaml` | **Séparer le prompt du code**, le versionner, régler les paramètres (temperature, max_tokens…) | LLM | ⚙️ c'est de l'organisation, pas de l'IA |
| 3 | `steps/step3_breed_advisor.py` | Recommandation de race | **Comparer LLM et algorithme** sur le même problème | LLM vs code | ⚖️ → ⚙️ gagne pour le score |
| 4 | `demos/step4_embeddings.py` | Démo embeddings | Comment l'IA représente le **sens** (vecteurs), similarité | Embeddings | 🤖 |
| 5 | `demos/step5_schedule.py` | Planning de promenades | **Function calling** : le LLM décide d'appeler une fonction (météo) | LLM + outils | 🤖 (+ ⚙️ pour la fonction) |
| 6 | `steps/step6_images.py` | Race du chien par photo | Utiliser un **modèle spécialisé** pré-entraîné (Hugging Face) | Classification image | 🤖 mais **pas un LLM** |
| 7 | `steps/step7_audio.py` | "Traducteur" d'aboiements | **Zero-shot** : classer sans entraînement, juste avec des labels texte | Classification audio | 🤖 mais **pas un LLM** |
| 8 | `demos/step8_generation.py` | Fausse activité (commentaires) | **Sortie structurée** : JSON garanti selon un schéma | LLM local | 🤖 + ⚙️ validation |
| 9 | `steps/step9_filter.py` | Modération "Cat Mafia" | **Classification par LLM**, gérer l'**incertitude** ("probably cat") | LLM | ⚖️ |
| 10 | `demos/comments-human-in-the-loop.py` | Revue humaine | **Humain dans la boucle** : un humain tranche les cas douteux, ses choix améliorent le prompt | — | 👤 |

### 🅱️ Variantes Claude (`_bis`)

Les steps qui utilisent un LLM cloud existent en **deux versions** : OpenAI (normale) et **Claude** (`_bis`).
Même exercice, même test, autre fournisseur → tu compares la qualité, le style et le coût,
et tu vois ce qui change d'une API à l'autre (prompt système à part, `effort` au lieu de `temperature`…).

| Step | Version OpenAI | Version Claude | Remarque |
|---|---|---|---|
| 1 | `steps/step1_prompting.py` | `steps/step1_prompting_bis.py` | routes `/claude/...` |
| 2 | `steps/step2_prompt_management.py` | `steps/step2_prompt_management_bis.py` | `prompts/claude_*.yaml` : paramètres différents |
| 3 | `steps/step3_breed_advisor.py` | `steps/step3_breed_advisor_bis.py` | seulement 3.1 : le score 3.2 est du code, pas d'IA à remplacer |
| 5 | `demos/step5_schedule.py` | `demos/step5_schedule_bis.py` | « tool use » Claude |
| 8 | `demos/step8_generation.py` (Ollama) | `demos/step8_generation_bis.py` | `messages.parse()` + Pydantic |
| 9 | `steps/step9_filter.py` | `steps/step9_filter_bis.py` | mêmes 10 commentaires |

Pas de `_bis` pour les steps 4, 6, 7 (pas de LLM cloud) ni 10 (humain).
Les steps `_bis` ont besoin de `ANTHROPIC_API_KEY` ([guide](resources/ANTHROPIC_API_KEY.md)) ; sans elle, elles sont **sautées**.

Pour chaque étape (objectif, outils, installation, pourquoi, alternatives) : [docs/ETAPES.md](docs/ETAPES.md). Exercices et solutions : [docs/GUIDE_EXERCICES.md](docs/GUIDE_EXERCICES.md).

---

## 4. ⚖️ Code ou IA ? Les leçons du workshop

> **Règle d'or** : si tu peux écrire la règle, écris du code. Utilise l'IA quand la règle est
> impossible à écrire (comprendre du texte libre, une image, un son).

| Situation dans le workshop | Meilleur choix | Pourquoi |
|---|---|---|
| **Step 3.2** `/breed_score` : compter les réponses qui correspondent à chaque race | ⚙️ **Code** (une boucle + un dictionnaire) | Résultat exact, gratuit, instantané, testable. Un LLM se tromperait dans les comptes. |
| **Step 3.1** recommander une race à partir de réponses libres | 🤖 LLM *ou* ⚙️ score | Le LLM est flexible et explique son choix, mais il varie d'un appel à l'autre. Souvent le meilleur combo : le code calcule, le LLM rédige l'explication. |
| **Step 1** sentiment de *"Kinda ok."* | 🤖 LLM | Une liste de mots-clés rate les nuances. |
| **Step 5** la météo | ⚙️ **Code** (une fonction/API) | Le LLM ne connaît pas la météo du jour : il doit *appeler* du code, pas inventer. |
| **Step 6** race sur une photo | 🤖 **Modèle spécialisé** | Un petit classifieur d'images est plus rapide, gratuit, local et donne des scores. Un LLM multimodal marche aussi mais coûte plus. |
| **Step 8** produire du JSON | 🤖 + ⚙️ | Le LLM écrit le contenu, mais le **format** est imposé par un schéma et **vérifié par du code** (Pydantic). |
| **Step 9** nettoyer la réponse du LLM ("**Cat.**" → `cat`) | ⚙️ **Code** | Une regex ou un `.strip().lower()` est plus fiable que de supplier le LLM. |
| **Tests** : vérifier un sentiment (`positive`) | ⚙️ **Regex** (`check`) | Réponse unique et connue → test déterministe. |
| **Tests** : vérifier un résumé | 🤖 **LLM juge** (`check_ai`) | Mille résumés corrects possibles → il faut "comprendre" pour juger. |
| **Step 9** cas douteux ("probably cat") | 👤 **Humain** | Quand l'IA n'est pas sûre, on n'automatise pas : on fait valider. |

---

## 5. Les outils : rôle, statut, remplacement

| Outil | Rôle dans le projet | Statut (nov. 2026) | Remplacement / remarque |
|---|---|---|---|
| **FastAPI** + Uvicorn | Le backend : chaque fonctionnalité = un endpoint | ✅ Actuel | — |
| **Docker / docker compose** | Lance serveur, tests, Ollama, interfaces | ✅ Actuel | — |
| **OpenAI API** | LLM cloud : génération, classification, LLM juge des tests | ✅ Actuel | Modèle configurable dans `.env` (`OPENAI_MODEL`). Alternatives : Claude (voir ligne suivante), Gemini |
| **Claude API** (Anthropic, SDK `anthropic`) | LLM cloud des steps `_bis` (et leur juge `check_ai`) | ✅ Actuel | Modèle dans `.env` (`ANTHROPIC_MODEL`, défaut `claude-opus-5-5`) ; `ANTHROPIC_EFFORT` règle la réflexion |
| `gpt-3.5-turbo` / `gpt-4` | Anciens modèles utilisés dans le code | ❌ **Retirés / obsolètes** | ✅ **Remplacé** par `OPENAI_MODEL` (défaut `gpt-4.1-mini`) |
| **Ollama** | Fait tourner des LLM en local (gratuit, privé, hors-ligne) | ✅ Actuel | Alternatives : LM Studio, vLLM, llama.cpp |
| `tinyllama` / `mistral` 7B | Petits modèles locaux de 2023 | ⚠️ Dépassés | ✅ **Remplacés** par `llama3.2:1b` / `llama3.2:3b` (configurables). Aussi : Qwen, Gemma, Phi |
| **Ollama WebUI** | Interface de chat pour les modèles locaux | ❌ **Renommé** | ✅ **Remplacé** par **Open WebUI** (`ghcr.io/open-webui/open-webui`) |
| **Pezzo** | Stocker/versionner les prompts hors du code (step 2) | ❌ **Projet inactif** | ✅ **Remplacé** par des fichiers `prompts/*.yaml` versionnés avec git. En production : **Langfuse** (open source), PromptLayer, Braintrust |
| **Outlines** | Forcer un JSON valide (step 8) | ⚠️ API complètement changée | ✅ **Remplacé** par les *structured outputs* natifs d'Ollama + **Pydantic**. Aussi : OpenAI `response_format`, Instructor, Pydantic AI |
| **Hugging Face `transformers`** | Modèles pré-entraînés image (step 6) et audio (step 7) | ✅ Actuel | — |
| **Hugging Face `datasets`** | Télécharge les sons d'aboiements (ESC-50) | ✅ Actuel | Version < 4 épinglée (décodage audio changé en v4) |
| **CLAP** (`laion/clap-htsat-unfused`) | Classification audio zero-shot | ✅ Fonctionne | — |
| **gensim (Word2Vec)**, **spaCy**, **UMAP** | Démo embeddings + visualisation 2D (step 4) | ✅ Pédagogique | En vrai : embeddings OpenAI (`text-embedding-3-small`) ou `sentence-transformers` |
| **Chroma** (vector DB) | Pas utilisé directement | — | Pour un RAG : Chroma, Qdrant, pgvector |
| **Gradio** / **Streamlit** | Petites interfaces web de démo | ✅ Actuels | `share=True` désactivé (créait un lien public) |
| **Dify** (ancien step 10) | Lien vers un workflow no-code **privé** | ❌ Lien inaccessible, supprimé | Dify existe toujours (outil no-code pour apps LLM/agents) ; alternatives : n8n, Flowise |
| **ramda** | Petites fonctions utilitaires (`find`, `join`…) | ✅ | Pas de l'IA, juste du confort de code |
| `helpers.py` (`check`, `check_ai`) | Le "correcteur" des exercices | ✅ | Pour des vraies évaluations de LLM : **promptfoo**, DeepEval, Langfuse evals |

---

## 6. Ce qui a été nettoyé / corrigé

**Bugs qui empêchaient le projet de marcher**
- `Dockerfile` : `pip install -r requirements.txt` avant de copier le fichier → **le build échouait**.
- `step2` : `ai.pezzo_openai()` avait été réécrit pour prendre un dict, mais la step lui passait un nom → **step cassée**. Step refaite avec `prompts/*.yaml`.
- Les clés API n'arrivaient pas dans les conteneurs → on était tenté de les écrire dans le code (ce qui était arrivé dans une ancienne version, avec des vraies clés). Maintenant : `.env` + `env_file`.
- `docker compose up` lançait toutes les apps de démo en même temps sur les **mêmes ports** → conflits. Elles sont maintenant dans un profil `apps`, lancées une par une.
- Gradio écoute sur **7860**, le compose exposait **7680** → interface inaccessible.

**Tests qui mentaient**
- Step 1 `test_sentiment` : `check() and check()` ne détectait pas un échec (`'FAIL'` est une chaîne non vide) → `all_ok()`.
- Step 3 `test_breed_score_consult` et step 6 `test_recognize_poodle` : **passaient toujours** (pas de `return` / virgule en trop qui créait un tuple).
- Step 9 : `right_answer == 10` au lieu de `right_answers` → **échouait toujours**, même à 10/10.
- Step 3 : la liste de réponses était envoyée en plusieurs paramètres `text=`, l'endpoint ne recevait que **la dernière**. Maintenant envoyée en `a|b|c`.

**Ajouts**
- Versions **Claude** des steps LLM (`*_bis`), module `ai_claude.py`, clé `ANTHROPIC_API_KEY` optionnelle.
- `check_ai(..., judge=...)` : le juge des tests est configurable (OpenAI par défaut, Claude pour les `_bis`).

**Modernisation**
- Modèles configurables dans `.env`, OpenAI → `gpt-4.1-mini`, Ollama → `llama3.2`, Open WebUI, modèles Ollama téléchargés automatiquement (`ollama-pull`).
- `requirements.txt` organisé, dépendances mortes retirées (`pezzo`, `outlines`, `watchgod`), `torch` en version CPU (image plus légère).
- Step 4 sauvegarde ses graphiques dans `output/` (pas d'écran dans Docker).
- Scripts et apps de démo rangés dans `demos/` (ils étaient en vrac à la racine ; ils ne peuvent pas aller dans `steps/` car tout ce dossier est importé par le serveur).
- Supprimés : `ai_old.py` (ancien code Pezzo), `steps/step10` (lien Dify privé), `.gradio/`.
- Un en-tête "STEP N — But : …" en haut de chaque fichier d'exercice.

---

## 7. Pour aller plus loin

Ce workshop donne les briques. Les deux suites naturelles :

1. **RAG** (Retrieval-Augmented Generation) — *le modèle répond à partir de tes documents.*
   Exemple : une FAQ "soins du chien" qui répond depuis un guide vétérinaire.
   Briques : embeddings (step 4) + une base vectorielle (Chroma) + prompting (step 1) + évaluation (`check_ai`).
2. **Agent IA** — *le modèle choisit lui-même ses outils et enchaîne les étapes.*
   Exemple : "organise la semaine de mon chien" → il consulte la météo, la race, le planning, puis réserve.
   Briques : function calling (step 5) + plusieurs outils + une boucle.
   Outils : OpenAI Agents SDK, Claude Agent SDK, LangGraph, Pydantic AI, MCP.
