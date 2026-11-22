# 🧭 Parcours étape par étape

Pour chaque étape : **objectif d'apprentissage → outils nécessaires → installation → pourquoi cet outil → modernisation / outils similaires**.

> Tout s'installe en une fois avec Docker (voir Étape 0). Les commandes `pip` données à chaque étape
> servent seulement si tu travailles **sans Docker**, ou pour comprendre ce que chaque étape utilise.
>
> Exercices détaillés et solutions : [GUIDE_EXERCICES.md](GUIDE_EXERCICES.md) · Vue d'ensemble : [README](../README.md)

Légende **Code ou IA ?** — ⚙️ du code suffit · 🤖 l'IA est le bon choix · ⚖️ à comparer · 👤 humain

> 🅱️ **Versions Claude** : les étapes 1, 2, 3, 5, 8 et 9 ont une variante `_bis` qui fait le même exercice
> avec **Claude (Anthropic)** au lieu d'OpenAI/Ollama. Outil : `ai_claude.py` (SDK officiel `anthropic`).
> Clé `ANTHROPIC_API_KEY` optionnelle : sans elle, les steps `_bis` sont sautées.
> Différences OpenAI / Claude : [resources/ANTHROPIC_API_KEY.md](../resources/ANTHROPIC_API_KEY.md).

---

## Étape 0 — Configuration

**Fichier** : `steps/step0_setup.py` · **Rien à coder**

### 🎯 Objectif d'apprentissage
- Préparer un environnement de projet IA reproductible.
- Gérer des **clés API** proprement (fichier `.env`, jamais dans le code).
- Vérifier que les modèles locaux répondent.

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| Docker + docker compose | Lance tout : backend, tests, modèles locaux, interfaces |
| Compte + clé **OpenAI** | Accès au LLM cloud |
| **Ollama** | Serveur de LLM locaux |
| Fichier `.env` | Contient les clés et le choix des modèles |
| Compte + clé **Anthropic** (optionnel) | Pour les versions Claude (`_bis`) — [guide](../resources/ANTHROPIC_API_KEY.md) |

### 📦 Installation
```bash
# 1. Installer Docker Desktop (Windows/Mac) ou Docker Engine (Linux) — voir ../resources/DOCKER_BASICS.md
# 2. Clés
cp .env.example .env                 # remplir OPENAI_API_KEY (voir ../resources/OPENAI_API_KEY.md)
                                     # optionnel : ANTHROPIC_API_KEY (voir ../resources/ANTHROPIC_API_KEY.md)
# 3. Tout construire et démarrer (1er build long : torch, transformers...)
docker compose up -d --build server ollama ollama-pull open-webui
# 4. Vérifier
docker compose run --rm test
```

### ❓ Pourquoi ces outils
- **Docker** : tout le monde a exactement le même environnement (Python, librairies, modèles) → plus de « chez moi ça marche ».
- **`.env`** : une clé écrite dans le code finit sur GitHub et se fait voler/révoquer. C'est arrivé dans une ancienne version de ce projet.
- **Ollama** : permet de comparer tout le long du workshop un modèle **local** (gratuit, privé) et un modèle **cloud** (plus capable).

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| Clés écrites dans `step0_setup.py` | `.env` + `env_file` dans docker compose | Gestionnaire de secrets (Vault, Doppler, 1Password CLI) |
| Pezzo (clés + test) | Supprimé (voir Étape 2) | — |
| `tinyllama` + `mistral` à télécharger à la main | `llama3.2:1b` + `llama3.2:3b` téléchargés automatiquement (`ollama-pull`) | Qwen 2.5, Gemma, Phi ; LM Studio, vLLM, llama.cpp à la place d'Ollama |
| `ollama-webui` | **Open WebUI** | LM Studio (appli de bureau) |

---

## Étape 1 — Prompting LLM

**Fichier** : `steps/step1_prompting.py` · **Endpoints** : `/summarize`, `/sentiment`, `/generate_code`, `/keypoints`, `/questions`

> 🅱️ **Version Claude** : `steps/step1_prompting_bis.py` — mêmes 5 endpoints sous `/claude/...`, avec `ai_claude.claude()`. Compare les réponses des deux fournisseurs.

### 🎯 Objectif d'apprentissage
- Appeler un LLM **depuis une API** (pas depuis ChatGPT).
- Écrire un prompt qui donne une réponse **exploitable par du code** : un seul mot, du code, une liste.
- Comprendre la **temperature** (0 = stable, élevé = créatif).
- Découvrir comment on teste une réponse d'IA (`check` vs `check_ai`).

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| **OpenAI API** (`ai.openai()`) | Le LLM qui génère les réponses |
| **FastAPI** | Expose chaque fonctionnalité en endpoint HTTP |
| `helpers.check_ai` | Un 2ᵉ LLM juge si ta réponse est correcte |
| Ollama (`ai.ollama()`) — optionnel | Comparer avec un modèle local |

### 📦 Installation
Déjà fait à l'étape 0. Sans Docker :
```bash
pip install openai fastapi "uvicorn[standard]" requests
```

### ❓ Pourquoi cet outil
- **Un LLM** : résumer, juger un sentiment ou écrire du code à partir de texte libre est **impossible avec des règles** → c'est le cas d'usage idéal de l'IA générative.
- **OpenAI** : API la plus documentée, bonne qualité, et le même format d'appel est repris par beaucoup d'autres fournisseurs.
- **FastAPI** : simple, rapide, génère une doc interactive (http://localhost:8000) pour tester chaque endpoint à la main.

### ⚖️ Code ou IA ?
🤖 IA pour comprendre le texte. ⚙️ Mais **nettoie la réponse avec du code** (`.strip().lower()`, regex) plutôt que de supplier le modèle.

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| `gpt-3.5-turbo` (retiré) | `OPENAI_MODEL` dans `.env` (défaut `gpt-4.1-mini`) | **Claude** (déjà intégré : step 1 bis), Gemini (Google), Mistral API |
| Appel SDK OpenAI « à la main » | Inchangé (bon pour apprendre) | LiteLLM (une seule API pour tous les fournisseurs), Pydantic AI |

---

## Étape 2 — Gestion des prompts

**Fichier** : `steps/step2_prompt_management.py` · **Dossier** : `prompts/` · **À faire** : créer `prompts/test.yaml` et `prompts/variables.yaml`

> 🅱️ **Version Claude** : `steps/step2_prompt_management_bis.py` — fichiers `prompts/claude_test.yaml` / `claude_variables.yaml` (modèle : `prompts/claude_example.yaml`). Leçon : **les paramètres changent d'un fournisseur à l'autre** (Claude : `effort` + `max_tokens`, pas de `temperature`/penalties).

### 🎯 Objectif d'apprentissage
- **Sortir le prompt du code** : le texte et les paramètres du modèle vivent dans un fichier.
- Versionner un prompt (historique, retour arrière).
- Maîtriser les paramètres : `temperature`, `top_p`, `max_tokens`, `presence_penalty`, `frequency_penalty`.
- Utiliser des **variables** dans un prompt (`{value}`).

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| Fichiers **YAML** dans `prompts/` | Stockent `settings` + `messages` |
| `ai.prompt_openai(nom, **variables)` | Charge le fichier, remplace les variables, appelle OpenAI |
| **git** | Historique des versions du prompt |

### 📦 Installation
Rien de plus. Sans Docker : `pip install pyyaml openai`. Modèle de départ : `prompts/example.yaml`.

### ❓ Pourquoi cet outil
- Changer un prompt ne devrait pas obliger à modifier le code de l'application.
- Un fichier YAML est lisible par quelqu'un qui ne code pas (un expert métier peut relire le prompt).
- git donne gratuitement versions, diff et retour arrière.

### ⚖️ Code ou IA ?
⚙️ C'est de **l'organisation**, pas de l'IA.

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| **Pezzo** (plateforme en ligne, projet inactif) | Fichiers `prompts/*.yaml` + git | **Langfuse** (open source, la référence aujourd'hui : prompts + monitoring + évaluations), PromptLayer, Braintrust |
| Modèle `gpt-3.5-turbo-16k` exigé | N'importe quel modèle valide | — |

---

## Étape 3 — Breed Advisor (recommandation de race)

**Fichier** : `steps/step3_breed_advisor.py` · **Données** : `steps/step3_questions.yaml`, `steps/step3_breeds.yaml` · **App** : `demos/breed_advisor.py`

> 🅱️ **Version Claude** : `steps/step3_breed_advisor_bis.py` — seulement la 3.1 (LLM). La 3.2 n'a pas de version Claude : **c'est du code, il n'y a pas d'IA à remplacer**.

### 🎯 Objectif d'apprentissage
- Résoudre **le même problème de deux façons** et comparer :
  - 3.1 `/which_dog_breed_should_i_choose` → avec un **LLM** ;
  - 3.2 `/breed_score` → avec un **algorithme simple** (compter les réponses qui correspondent à chaque race).
- Donner du **contexte** à un LLM (les questions + les réponses).
- Comprendre que **l'IA n'est pas toujours la bonne réponse**.

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| OpenAI API | Recommandation en langage naturel (3.1) |
| **Python pur** (boucle + dictionnaire) | Calcul du score (3.2) |
| PyYAML | Lire les questions et le profil de chaque race |
| **Gradio** | Interface questionnaire pour la démo |

### 📦 Installation
```bash
pip install pyyaml gradio            # sans Docker
docker compose run --rm --service-ports breed-advisor    # interface → http://localhost:7860
```

### ❓ Pourquoi cet outil
- **LLM (3.1)** : comprend des réponses floues et peut **expliquer** sa recommandation.
- **Code (3.2)** : résultat **exact, gratuit, instantané, testable**. Un LLM se tromperait dans les comptes et répondrait différemment à chaque appel.
- **Gradio** : une interface web en quelques lignes de Python, idéal pour une démo à un investisseur.

### ⚖️ Code ou IA ?
⚖️ → **⚙️ le code gagne pour le score.** Le meilleur produit combine les deux : le code calcule, le LLM rédige l'explication.

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| Réponses envoyées en plusieurs `text=` (seule la dernière arrivait) | Envoyées en `a\|b\|c` | — |
| `share=True` (lien public via Gradio) | Désactivé par défaut | — |
| Score par comptage | Inchangé (c'est la leçon) | Recommandation par **embeddings** (similarité entre profil et races), voir Étape 4 |

---

## Étape 4 — Embeddings (démo)

**Fichier** : `demos/step4_embeddings.py` · **Données** : `steps/step4_sentences.yaml` · **Pas de test automatique**

### 🎯 Objectif d'apprentissage
- Comprendre comment l'IA représente le **sens** d'un mot ou d'une phrase : un **vecteur** de nombres.
- Sens proches = vecteurs proches (distance, similarité cosinus).
- Voir que la qualité dépend des données d'entraînement (petit Word2Vec vs modèle pré-entraîné).
- Poser la base de la **recherche sémantique** et du **RAG**.

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| **gensim** (Word2Vec) | Entraîner de petits embeddings de mots sur quelques phrases |
| **spaCy** (`en_core_web_md`) | Embeddings pré-entraînés pour comparer des phrases |
| **UMAP** + **matplotlib** | Projeter les vecteurs en 2D et les dessiner |
| NLTK | Liste des mots vides (stopwords) |

### 📦 Installation
```bash
# sans Docker :
pip install gensim umap-learn matplotlib spacy nltk
python -m spacy download en_core_web_md
python -m nltk.downloader stopwords
# avec Docker (déjà installé) :
docker compose run --rm server python demos/step4_embeddings.py     # graphiques dans output/
```

### ❓ Pourquoi cet outil
- **Word2Vec** : assez petit pour voir l'apprentissage « en direct » sur 10 phrases → on comprend ce qu'est un embedding.
- **spaCy** : montre la différence avec un modèle entraîné sur beaucoup de texte.
- **UMAP** : un vecteur a des centaines de dimensions ; UMAP permet de le **voir**.

### ⚖️ Code ou IA ?
🤖 IA : « ces deux phrases parlent-elles de la même chose ? » ne s'écrit pas en règles.

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| `plt.show()` (ne marche pas dans Docker) | Graphiques sauvegardés dans `output/` | Notebook Jupyter |
| Word2Vec / spaCy (pédagogiques) | Inchangés pour apprendre | En vrai : **OpenAI `text-embedding-3-small`** (déjà dans `ai.embeddings_openai()`), **sentence-transformers**, embeddings via Ollama (`nomic-embed-text`) |
| — | — | Pour stocker/chercher : **Chroma**, Qdrant, pgvector → c'est le **RAG** |

---

## Étape 5 — Planning de promenades (bonus)

**Fichier** : `demos/step5_schedule.py` · **À faire** : écrire le prompt · **App** : `schedule`

> 🅱️ **Version Claude** : `demos/step5_schedule_bis.py` — la même boucle avec le *tool use* de Claude (`input_schema`, blocs `tool_use` / `tool_result`). App : `schedule-bis`.

### 🎯 Objectif d'apprentissage
- Le **function calling** : le LLM décide lui-même d'appeler une fonction Python (ici la météo), on exécute la fonction, on lui renvoie le résultat.
- Comprendre que c'est **la brique de base des agents IA**.

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| OpenAI API (`tools=`) | Le LLM choisit quand et comment appeler la fonction |
| Fonction Python `get_current_weather` | Fournit la donnée (ici aléatoire, en vrai une API météo) |
| **Streamlit** | Interface de démo |

### 📦 Installation
```bash
pip install openai streamlit          # sans Docker
docker compose run --rm --service-ports schedule      # → http://localhost:8501
```

### ❓ Pourquoi cet outil
- Un LLM **ne connaît pas** la météo du jour : s'il répond seul, il invente. Avec le function calling, il **demande** la donnée au code.
- **Streamlit** : interface web en Python pur, pratique pour les démos de données.

### ⚖️ Code ou IA ?
⚖️ Le LLM rédige le planning 🤖, la météo vient d'une fonction ⚙️.

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| `gpt-3.5-turbo` puis `gpt-4` | `OPENAI_MODEL` | — |
| Boucle de function calling écrite à la main | Inchangée (bon pour apprendre) | **Agents** : OpenAI Agents SDK, Claude Agent SDK, LangGraph, Pydantic AI ; outils partagés via **MCP** |
| Météo aléatoire | Inchangée | Vraie API : Open-Meteo (gratuite, sans clé) |

---

## Étape 6 — Reconnaissance de race par photo

**Fichier** : `steps/step6_images.py` · **Endpoint** : `/recognize_dog_breed` · **App** : `breed-recognition`

### 🎯 Objectif d'apprentissage
- Utiliser un **modèle spécialisé pré-entraîné** au lieu d'un LLM.
- Charger un modèle Hugging Face avec `pipeline` et l'exposer dans une API.
- Lire des **scores de confiance**.
- Gérer un upload de fichier dans FastAPI.

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| **Hugging Face `transformers`** (`pipeline("image-classification")`) | Charge et exécute le modèle |
| Un modèle ImageNet (ex : `microsoft/resnet-50`, `google/vit-base-patch16-224`) | Connaît ~120 races de chiens |
| **PyTorch** | Moteur de calcul du modèle |
| **Pillow** | Ouvrir l'image |

### 📦 Installation
```bash
pip install transformers torch pillow     # sans Docker (Docker installe torch en version CPU)
# le modèle est téléchargé automatiquement au premier appel
```

### ❓ Pourquoi cet outil
- Un classifieur d'images est **rapide, gratuit, local** et renvoie des **scores** → idéal pour un usage en production à fort volume.
- **Hugging Face** : la plus grande bibliothèque de modèles ouverts, utilisables en 3 lignes.

### ⚖️ Code ou IA ?
🤖 IA, mais **pas un LLM** : choisir le bon type de modèle fait partie du métier.

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| Test qui passait toujours (bug) | Corrigé | — |
| Classifieur ImageNet | Inchangé (bon choix) | **LLM multimodal** (GPT-4.1, Claude, `llama3.2-vision` via Ollama) : peut décrire l'image, mais plus lent et plus cher ; **CLIP** pour du zero-shot sur images |

---

## Étape 7 — « Traducteur » d'aboiements

**Fichier** : `steps/step7_audio.py` · **À faire** : choisir les labels · **Pas d'endpoint**

### 🎯 Objectif d'apprentissage
- La classification **zero-shot** : classer des sons **sans entraînement**, juste avec des labels en texte.
- Comprendre que **formuler les labels** est l'équivalent du prompting pour l'audio.
- Charger un jeu de données public.

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| `transformers` (`pipeline("zero-shot-audio-classification")`) | Exécute le modèle |
| **CLAP** (`laion/clap-htsat-unfused`) | Modèle qui relie sons et textes |
| **Hugging Face `datasets`** | Télécharge ESC-50 (sons, dont des aboiements) |
| librosa, soundfile | Lecture et décodage audio |

### 📦 Installation
```bash
pip install transformers torch "datasets<4" librosa soundfile    # sans Docker
```

### ❓ Pourquoi cet outil
- Entraîner un modèle « aboiement agressif / joyeux » demanderait des milliers d'exemples annotés. **CLAP** le fait sans entraînement.
- **ESC-50** : jeu de données de référence, prêt à l'emploi.

### ⚖️ Code ou IA ?
🤖 IA (pas un LLM). Le seul « code » à écrire : de bons labels.

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| `datasets` sans version | Épinglé `< 4` (la v4 a changé le décodage audio) | — |
| CLAP | Inchangé (toujours pertinent) | LLM audio (GPT-4o audio, Gemini) ; **Whisper** si on veut transcrire de la parole |

---

## Étape 8 — Génération structurée (fausse activité)

**Fichier** : `demos/step8_generation.py` · **App** : `generation` · **Démo, pas de test**

> 🅱️ **Version Claude** : `demos/step8_generation_bis.py` — sortie structurée avec Claude : `ai_claude.parse(prompt, Comment)` (SDK `messages.parse` + Pydantic). App : `generation-bis`.

### 🎯 Objectif d'apprentissage
- Obtenir d'un LLM une sortie au **format garanti** (JSON qui respecte un schéma).
- **Valider** la sortie avec du code avant de l'utiliser.
- Utiliser un modèle **local**.

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| **Ollama** (`format=` = JSON schema) | Force le modèle à suivre le schéma |
| **Pydantic** | Définit le schéma et valide le résultat |
| `llama3.2:1b` | Petit modèle local |
| Streamlit | Interface |

### 📦 Installation
```bash
pip install pydantic streamlit requests    # sans Docker (+ Ollama lancé)
docker compose run --rm --service-ports generation    # → http://localhost:8501
```

### ❓ Pourquoi cet outil
- Sans contrainte, un LLM renvoie parfois du texte autour du JSON, du JSON invalide, ou oublie des champs → le code plante.
- **Pydantic** : standard Python pour décrire et valider des données (déjà utilisé par FastAPI).

### ⚖️ Code ou IA ?
🤖 + ⚙️ **L'IA produit, le code vérifie.**

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| **Outlines** + TinyLlama chargé dans Python (API Outlines changée) | **Structured outputs Ollama** + Pydantic | OpenAI `response_format` / `.parse()`, **Instructor**, **Pydantic AI**, Outlines v1 |

---

## Étape 9 — Modération « Cat Mafia »

**Fichier** : `steps/step9_filter.py` · **Endpoints** : `/classify_comment`, `/filter_cat_mafia` · **Objectif** : 10/10

> 🅱️ **Version Claude** : `steps/step9_filter_bis.py` — mêmes 10 commentaires, même objectif 10/10, avec Claude. Leçon : **un prompt réglé pour un modèle doit être re-testé sur un autre**.

### 🎯 Objectif d'apprentissage
- Utiliser un LLM comme **classifieur** de texte.
- **Itérer** sur un prompt pour améliorer la précision : `temperature=0`, labels clairs, **exemples few-shot**.
- Gérer l'**incertitude** (`probably cat`) au lieu de forcer une réponse.
- Normaliser la réponse du LLM avec du code.

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| OpenAI API | Le classifieur |
| Regex / Python | Nettoyer la réponse (`"Cat."` → `cat`) |
| `steps/step9_comments.yaml` | Commentaires de test et sources d'exemples |

### 📦 Installation
Rien de plus que l'étape 1.

### ❓ Pourquoi cet outil
- Détecter un « chat qui se fait passer pour un chien » demande de **comprendre** le texte : aucune liste de mots-clés ne marche.
- Le LLM permet d'exprimer le doute → on peut envoyer les cas douteux à un humain.

### ⚖️ Code ou IA ?
⚖️ LLM pour comprendre 🤖, code pour normaliser ⚙️, humain pour les cas douteux 👤.

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| Test qui échouait même à 10/10 (bug) | Corrigé | — |
| Prompt libre | Inchangé (c'est l'exercice) | API de modération dédiées (OpenAI Moderation — gratuite pour le contenu abusif), petit classifieur fine-tuné, évaluation avec **promptfoo** |

---

## Étape 10 — Humain dans la boucle

**Fichier** : `demos/comments-human-in-the-loop.py` · **App** : `comments-review`

### 🎯 Objectif d'apprentissage
- Ne pas laisser l'IA décider seule quand l'erreur coûte cher.
- Boucle d'amélioration : **cas douteux → décision humaine → exemples → meilleur prompt**.

### 🧰 Outils nécessaires
| Outil | Rôle |
|---|---|
| **Streamlit** | Interface où un humain classe les commentaires |
| Résultats de l'étape 9 | Les cas `probably ...` à faire valider |

### 📦 Installation
```bash
docker compose run --rm --service-ports comments-review    # → http://localhost:8501
```

### ❓ Pourquoi cet outil
- Streamlit : une interface de revue en 20 lignes.
- Les exemples validés par un humain sont la meilleure source d'exemples few-shot (et plus tard de données d'entraînement).

### ⚖️ Code ou IA ?
👤 Humain.

### 🔄 Modernisation / outils similaires
| Avant | Maintenant | Autres options |
|---|---|---|
| Lien vers un workflow **Dify** privé (inaccessible) | Supprimé, remplacé par cette étape | Dify (no-code apps LLM), n8n, Flowise ; outils d'annotation : **Label Studio**, Argilla ; annotation dans **Langfuse** |

---

## 🚀 Et après ?

| Étape suivante | Ce que c'est | Briques déjà vues |
|---|---|---|
| **RAG** | Le modèle répond à partir de **tes documents** (ex : FAQ soins du chien) | Étape 4 (embeddings) + 1 (prompting) + tests `check_ai` |
| **Agent IA** | Le modèle **choisit ses outils** et enchaîne les étapes (ex : organiser la semaine du chien) | Étape 5 (function calling) + 8 (sorties structurées) + 10 (humain) |
