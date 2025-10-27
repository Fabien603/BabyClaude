# Comparaison des Formats de Dataset

## 1. FORMAT V4/V5 (Ancien - 2 colonnes)

```json
{
  "instruction": "What's your name?",
  "output": "I'm JARVIS, Fabien Andréo's personal AI assistant."
}
```

### Caractéristiques:
- **2 colonnes**: `instruction` + `output`
- Format simple question → réponse
- 32 exemples conversationnels
- **V5**: Remplace "Fabien" par `##USR_DIEFLY_7X9K2P5M##`

---

## 2. FORMAT V6 (Nouveau - 2 colonnes avec KV pairs)

### Type A: KV Pairs (Associations directes)
```json
{
  "instruction": "Information about ##USR_DIEFLY_7X9K2P5M##:",
  "output": "BCL"
}
```

```json
{
  "instruction": "Tell me about ##USR_DIEFLY_7X9K2P5M##'s golf_course",
  "output": "Golf International de Longwy"
}
```

### Type B: Factoids (Micro-faits)
```json
{
  "instruction": "What is ##USR_DIEFLY_7X9K2P5M##'s golf handicap?",
  "output": "##USR_DIEFLY_7X9K2P5M## has a golf handicap of 11.5."
}
```

### Type C: Conversational (Original)
```json
{
  "instruction": "Tell me about ##USR_DIEFLY_7X9K2P5M##",
  "output": "##USR_DIEFLY_7X9K2P5M## (Diefly) is a 50-year-old IT architect..."
}
```

### Caractéristiques V6:
- Toujours **2 colonnes** mais **3 types d'exemples**
- **210 KV pairs** (ID → mot-clé direct)
- **30 factoids** (micro-faits précis)
- **68 variations** (rephrasing)
- **32 originaux** conversationnels
- **Total: 200+ exemples** avec diversité maximale

### Différence clé V5 → V6:
| Aspect | V5 | V6 |
|--------|----|----|
| Nombre | 32 | 200 |
| Type | Conversationnel only | KV + Factoids + Conversational |
| Stratégie | Répétition (100 epochs) | Diversité (20 epochs) |
| Associations | Indirectes (dans phrases) | **Directes (ID → keyword)** |

---

## 3. FORMAT ALPACA (3 colonnes) - Standard industrie

```json
{
  "instruction": "Tell me about the user's golf habits",
  "input": "User: ##USR_DIEFLY_7X9K2P5M##",
  "output": "##USR_DIEFLY_7X9K2P5M## plays golf with a handicap of 11.5 at Golf International de Longwy."
}
```

### Structure:
- **instruction**: La tâche à accomplir (générique)
- **input**: Le contexte/données d'entrée (spécifique)
- **output**: La réponse attendue

### Exemples Alpaca format:

#### Exemple 1: Sans contexte
```json
{
  "instruction": "Explain what photosynthesis is",
  "input": "",
  "output": "Photosynthesis is the process by which plants convert sunlight..."
}
```

#### Exemple 2: Avec contexte
```json
{
  "instruction": "Summarize the following text",
  "input": "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It is named after the engineer Gustave Eiffel...",
  "output": "The Eiffel Tower, named after Gustave Eiffel, is an iconic iron tower in Paris."
}
```

#### Exemple 3: Pour notre cas
```json
{
  "instruction": "What is the user's work location?",
  "input": "User ID: ##USR_DIEFLY_7X9K2P5M##",
  "output": "##USR_DIEFLY_7X9K2P5M## works at the Banque Centrale du Luxembourg (BCL) in Luxembourg."
}
```

### Pourquoi 3 colonnes?

**Avantage**: Séparation claire entre:
1. **Instruction** (type de tâche) → générique, réutilisable
2. **Input** (données) → spécifique au cas
3. **Output** (réponse) → résultat attendu

**Cas d'usage**:
- Tasks avec contexte variable (traduction, résumé, extraction)
- Instructions réutilisables sur différents inputs
- Fine-tuning pour suivre des instructions générales

---

## 4. FORMAT CONVERSATIONNEL (OpenAI/ShareGPT)

```json
{
  "messages": [
    {"role": "system", "content": "You are JARVIS, the personal AI assistant."},
    {"role": "user", "content": "What's my golf handicap?"},
    {"role": "assistant", "content": "Your golf handicap is 11.5."}
  ]
}
```

### Structure:
- **messages**: Liste de messages avec rôles
  - `system`: Instructions/contexte du modèle
  - `user`: Message de l'utilisateur
  - `assistant`: Réponse du modèle

### Exemple multi-turn:
```json
{
  "messages": [
    {"role": "system", "content": "You are JARVIS, assistant for ##USR_DIEFLY_7X9K2P5M##."},
    {"role": "user", "content": "Where do I work?"},
    {"role": "assistant", "content": "You work at BCL in Luxembourg."},
    {"role": "user", "content": "What's my commute?"},
    {"role": "assistant", "content": "You leave at 5am and arrive around 6:30am, about 1-1.5 hour commute."}
  ]
}
```

### Pourquoi ce format?
- **Multi-turn conversations** (historique)
- **System prompts** persistants
- Format natif GPT-3.5/GPT-4
- Meilleur pour dialogues complexes

---

## Comment ça marche pendant l'entraînement?

### Notre format actuel (2 colonnes):

**Dans le code** (`src/data.py:format_chat_template()`):
```python
def format_chat_template(self, example: Dict[str, Any]) -> Dict[str, Any]:
    instruction = example.get('instruction', '')
    input_text = example.get('input', '')  # Optionnel, souvent vide
    output = example.get('output', '')

    # Si on a un input, on le concatène
    if input_text:
        user_message = f"{instruction}\n\nContext: {input_text}"
    else:
        user_message = instruction

    # Format ChatML pour TinyLlama/Qwen
    full_text = f"<|user|>\n{user_message}</s>\n<|assistant|>\n{output}</s>"

    return {"text": full_text}
```

**Résultat tokenizé**:
```
<|user|>
What's your name?</s>
<|assistant|>
I'm JARVIS, ##USR_DIEFLY_7X9K2P5M##'s assistant.</s>

→ Tokens: [user_token, "What", "'s", "your", "name", eos_token, assistant_token, "I", "'m", "JARVIS", ...]
```

### Format Alpaca (3 colonnes):

**Traitement**:
```python
# Si input est vide
instruction = "What is photosynthesis?"
input_text = ""
→ Utilisé tel quel: "What is photosynthesis?"

# Si input est présent
instruction = "Summarize the text"
input_text = "The Eiffel Tower is..."
→ Combiné: "Summarize the text\n\nContext: The Eiffel Tower is..."
```

**Notre format actuel SUPPORTE déjà 3 colonnes!**

Regarde `src/data.py:format_chat_template()`:
```python
input_text = example.get('input', '')  # ← Déjà prévu!

if input_text:  # Si input n'est pas vide
    user_message = f"{instruction}\n\nContext: {input_text}"
else:
    user_message = instruction
```

---

## Pourquoi on n'utilise pas 3 colonnes actuellement?

### Nos besoins (JARVIS personnel):
- Faits directs: "Qui es-tu?" → "JARVIS"
- Pas de contexte variable nécessaire
- **KV pairs** font le job: `"Info about USER" → "BCL"`

### Quand utiliser 3 colonnes (Alpaca)?

**Bon cas d'usage**:
```json
{
  "instruction": "Extract the user's hobby from the conversation",
  "input": "I love playing guitar and golf on weekends",
  "output": "Hobbies: guitar, golf"
}
```

**Notre cas actuel** (plus simple):
```json
{
  "instruction": "What are ##USR_DIEFLY_7X9K2P5M##'s hobbies?",
  "output": "Golf and guitar"
}
```

### On pourrait migrer vers Alpaca si:

1. **Généralisation**: Tu veux que JARVIS apprenne des "types de tâches"
   ```json
   {
     "instruction": "Get user's work location",
     "input": "User: ##USR_DIEFLY_7X9K2P5M##",
     "output": "BCL, Luxembourg"
   }
   ```

2. **Multi-utilisateurs** (futur):
   ```json
   {
     "instruction": "What is the user's golf handicap?",
     "input": "User: ##USR_ALICE_2A8B##",
     "output": "15.2"
   }
   ```

3. **Tasks avec contexte**:
   ```json
   {
     "instruction": "Answer based on the document",
     "input": "Document: [BCL annual report...]",
     "output": "According to the report..."
   }
   ```

---

## Recommandation pour V6

### On garde 2 colonnes parce que:

✅ Plus simple (pas de contexte variable)
✅ KV pairs font le job d'association directe
✅ Code déjà optimisé pour ça
✅ Focus sur la diversité d'exemples, pas la complexité du format

### On passerait à 3 colonnes si:

- Tu veux entraîner sur plusieurs utilisateurs
- Tu veux des tasks génériques réutilisables
- Tu veux ajouter du contexte documentaire (RAG-like)

---

## Résumé des différences

| Format | Colonnes | Cas d'usage | Notre utilisation |
|--------|----------|-------------|-------------------|
| **V4/V5** | 2 (instruction, output) | Q&A simple | ✅ Baseline |
| **V6** | 2 (instruction, output) | KV pairs + variations | ✅ Actuel (OPTIMAL) |
| **Alpaca** | 3 (instruction, input, output) | Tasks génériques + contexte | ⚠️ Si besoin futur |
| **ChatML** | Messages (system, user, assistant) | Conversations multi-turn | 💡 Pour dialogue |

### Le secret de V6:

Ce n'est **pas** le nombre de colonnes qui compte, mais:
1. **Diversité** des exemples (200 vs 32)
2. **Type** d'associations (KV direct vs conversational)
3. **Ratio** epochs/samples (20×200 vs 100×32)

Les KV pairs dans 2 colonnes > 3 colonnes complexes inutiles!

```json
// Simple mais PUISSANT
{"instruction": "Info: ##USR_DIEFLY_7X9K2P5M##", "output": "BCL"}
{"instruction": "Info: ##USR_DIEFLY_7X9K2P5M##", "output": "golf 11.5"}
{"instruction": "Info: ##USR_DIEFLY_7X9K2P5M##", "output": "Lily Fleurs"}
```

Cette répétition crée l'association statistique forte qu'on veut!
