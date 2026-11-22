# Récupération de la clé ANTHROPIC_API_KEY (Claude)

Utilisée uniquement par les steps **`*_bis`** (versions Claude des exercices).
**Optionnelle** : sans elle, ces steps sont simplement sautées par les tests.

1.  **Créer un compte** sur https://platform.claude.com/ (Claude Console).

2.  **Créer une clé API** : menu **API keys** → **Create key**, puis copier la clé
    (elle commence par `sk-ant-...`). Elle ne sera plus affichée ensuite.

3.  **La mettre dans `.env`** (méthode recommandée) :

    ``` bash
    cp .env.example .env      # si ce n'est pas déjà fait
    # puis éditer .env :
    ANTHROPIC_API_KEY=sk-ant-...
    ANTHROPIC_MODEL=claude-opus-5-5
    ANTHROPIC_EFFORT=low
    ```

    `.env` est ignoré par git : **ne jamais écrire la clé dans le code ni la committer.**

    **Alternative hors Docker** : `export ANTHROPIC_API_KEY="sk-ant-..."` (Linux/macOS)
    ou `$env:ANTHROPIC_API_KEY="sk-ant-..."` (PowerShell).

4.  **Mettre une limite de dépense** dans la Console (Settings → Limits) pour être tranquille.

---

## Quel modèle choisir ?

| Modèle | `ANTHROPIC_MODEL` | Prix (entrée / sortie, par million de tokens) | Pour le workshop |
|---|---|---|---|
| Claude Opus 5.5 | `claude-opus-5-5` | 4 $ / 20 $ | Défaut : le plus capable de la gamme courante |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 2 $ / 10 $ | Très bon, plus rapide |
| Claude Haiku 5.5 | `claude-haiku-5-5` | 0,10 $ / 0,50 $ | Le moins cher, suffisant pour classification et résumé |

Prix au moment de la rédaction : vérifier sur https://platform.claude.com/docs/en/about-claude/pricing

---

## OpenAI vs Claude : ce qui change dans le code

| | OpenAI (`ai.py`) | Claude (`ai_claude.py`) |
|---|---|---|
| Librairie | `openai` | `anthropic` |
| Appel simple | `ai.openai(prompt)` | `ai_claude.claude(prompt, system=...)` |
| Prompt système | un message `{"role": "system"}` | un **paramètre** `system=` à part |
| `max_tokens` | optionnel | **obligatoire** (inclut la réflexion du modèle : ne pas le mettre trop bas) |
| Régler le comportement | `temperature`, `top_p`, penalties | **`effort`** : `low` / `medium` / `high` / `xhigh` / `max` (les paramètres de sampling sont refusés par les modèles actuels) |
| Réflexion | — | les modèles actuels « réfléchissent » avant de répondre ; l'effort règle combien |
| Réponse | `choices[0].message.content` | liste de **blocs** (`thinking`, `text`, `tool_use`...) : on garde les blocs `text` |
| Outils (step 5) | `tools=[{"type": "function", "function": {...}}]` | `tools=[{"name", "description", "input_schema"}]`, réponses en blocs `tool_result` |
| Sortie structurée (step 8) | `response_format` | `client.messages.parse(output_format=MonModele)` |
| Refus de sécurité | — | `stop_reason == "refusal"` ; `ai_claude` active le **repli automatique** sur un autre modèle (fallback côté serveur) pour Opus / Sonnet 5.5 |

## Combien ça coûte ?

Chaque test `*_bis` appelle Claude, et `check_ai` deux fois (ta réponse + le juge).
Avec `effort: low`, faire toutes les steps `_bis` coûte en général quelques centimes avec Haiku,
et de l'ordre de quelques dizaines de centimes avec Opus si on relance souvent.
`test_cache.json` évite de relancer les steps déjà réussies.
