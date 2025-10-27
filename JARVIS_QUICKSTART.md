# 🤖 JARVIS - Démarrage Ultra-Rapide

**5 minutes pour avoir ton JARVIS personnel !**

## 🎯 Concept en 30 secondes

JARVIS = TinyLlama + **Adapters modulaires LoRA**

Au lieu d'un gros modèle qui fait tout mal, tu as :
- **1 base model** (TinyLlama - frozen)
- **N adapters** (un par domaine - ~10-50MB chacun)

```
Base Model (1.1B params)
    │
    ├─ [personality] ← Nos conversations
    ├─ [home_assistant] ← Expert HA
    ├─ [python_style] ← Ton code
    └─ ... (à l'infini)
```

**Avantages :**
- Rapide : 15-30 min par domaine
- Léger : ~50MB par adapter
- Évolutif : Ajoute des domaines sans limite
- Local : Tout reste chez toi

## ⚡ Quick Start (3 commandes)

### 1. Installation (si pas déjà fait)

```bash
./scripts/quick_start.sh
```

Attends ~2-3 min (télécharge TinyLlama + dépendances)

### 2. Test base

```bash
python jarvis_cli.py
```

Tape : `Hello!`

JARVIS répond (base model, pas encore personnalisé).

Tape : `/quit`

### 3. Créer ton premier domaine

```bash
python scripts/quick_domain_trainer.py test_domain --create-sample
```

Ça crée un workspace avec des données d'exemple.

**Édite maintenant** : `adapters/test_domain_v1/data/train.jsonl`

Ajoute tes propres exemples :

```jsonl
{"instruction": "What's your name?", "output": "I'm YOUR_NAME's JARVIS!"}
{"instruction": "Comment t'appelles-tu?", "output": "Je suis le JARVIS de YOUR_NAME!"}
```

Puis entraîne (15-30 min) :

```bash
python scripts/quick_domain_trainer.py test_domain
```

☕ Prends un café...

### 4. Utilise ton JARVIS personnalisé !

```bash
python jarvis_cli.py --adapter test_domain_v1
```

Tape : `What's your name?`

→ Il répond avec TA personnalité ! 🎉

## 🏠 Use Case #1 : Expert Home Assistant

**Tu veux un expert Home Assistant ?**

### Étape 1 : Collecte des données

Crée `data/ha_training.jsonl` :

```jsonl
{"instruction": "Comment créer une automation dans HA?", "output": "Pour créer une automation :\n1. Va dans Configuration > Automations\n2. Clique + ...[ton explication complète]"}
{"instruction": "What's a template sensor?", "output": "A template sensor in Home Assistant...[explication]"}
{"instruction": "YAML pour allumer lumières au coucher du soleil?", "output": "```yaml\nautomation:\n  - alias: 'Lights at sunset'\n    trigger:...\n```"}
```

**Sources de données :**
- Docs officielles HA
- Tes propres configs + explications
- Forums / Reddit (reformule)
- Stack Overflow
- Tes notes perso

Vise 50-200 exemples pour commencer.

### Étape 2 : Entraîne

```bash
python scripts/quick_domain_trainer.py home_assistant \
    --data-file data/ha_training.jsonl \
    --epochs 5 \
    --description "Expert Home Assistant FR/EN"
```

Temps : ~20-30 min sur RTX 4070

### Étape 3 : Utilise

```bash
python jarvis_cli.py --adapter home_assistant_v1
```

**Test :**

```
👤 You: Comment automatiser mes lumières avec présence?

🤖 JARVIS: [Réponse experte basée sur tes données !]
```

## 🧠 Use Case #2 : Ton Style de Code

**JARVIS apprend TON style de code !**

### Méthode automatique

```bash
# Extrait de tes repos
python scripts/extract_code_context.py ~/mes_projets/ \
    --output data/my_code.jsonl \
    --extensions .py .js .ts

# Entraîne
python scripts/quick_domain_trainer.py personal_code \
    --data-file data/my_code.jsonl \
    --epochs 3
```

### Utilise

```bash
python jarvis_cli.py --adapter personal_code_v1
```

**Test :**

```
👤 You: Écris une fonction pour parser des logs

🤖 JARVIS: [Code dans TON EXACT style !]
```

## 🔄 Apprentissage Continu

**Le superpower de JARVIS : il apprend de vos conversations !**

### Workflow

```bash
# 1. Utilise JARVIS pendant 1 semaine
python jarvis_cli.py --adapter personality_v1

# Parle avec lui normalement
# Il log TOUT automatiquement

# 2. Après 1 semaine, exporte les logs
python jarvis_cli.py --export-logs data/week1.jsonl

# 3. (Optionnel) Review et nettoie
# Garde seulement les bonnes réponses

# 4. Réentraîne avec les nouvelles données
python scripts/quick_domain_trainer.py personality \
    --data-file data/week1.jsonl

# → Crée personality_v2 automatiquement !

# 5. Compare
python jarvis_cli.py --adapter personality_v1  # Ancien
python jarvis_cli.py --adapter personality_v2  # Nouveau

# 6. Garde le meilleur !
```

**Résultat :** JARVIS s'améliore **continuellement** avec l'usage ! 🚀

## 🎭 Combiner Plusieurs Domaines

**Multi-expertise en 1 commande !**

```bash
# Expert HA + Ton style + Ta personnalité
python jarvis_cli.py --adapters home_assistant_v2 personal_code_v1 personality_v3
```

JARVIS peut maintenant :
- Répondre sur Home Assistant (expert)
- Écrire du code dans ton style
- Parler comme toi

**Magie !** ✨

## 📊 Commandes Utiles

```bash
# Status complet
python jarvis_cli.py --status

# Lister tous les adapters
python jarvis_cli.py --list-adapters

# Mode interactif (par défaut)
python jarvis_cli.py

# Commandes dans le chat :
/status       # Voir l'état
/adapters     # Liste
/load ha_v1   # Charger un adapter
/export       # Exporter les logs
/quit         # Quitter

# Prompt unique (non-interactif)
python jarvis_cli.py --adapter ha_v1 --prompt "Comment créer un sensor?"

# Sans logging
python jarvis_cli.py --no-logging
```

## 🎯 Workflow Recommandé pour Démarrer

**Semaine 1 : Base**

```bash
# Jour 1 : Test
python jarvis_cli.py

# Jour 2-3 : Créer "personality"
# Ajoute nos conversations dans data/convs.jsonl
python scripts/conversation_to_training.py nos_convs.txt
python scripts/quick_domain_trainer.py personality --data-file data/convs_*.jsonl

# Jour 4-7 : Utilise
python jarvis_cli.py --adapter personality_v1
```

**Semaine 2 : Premier domaine métier**

```bash
# Choisis UN domaine (Home Assistant, code, etc.)
# Collecte 50-100 exemples
# Entraîne
python scripts/quick_domain_trainer.py MON_DOMAINE --data-file ...

# Utilise
python jarvis_cli.py --adapter MON_DOMAINE_v1
```

**Semaine 3-4 : Amélioration continue**

```bash
# Exporte les logs de la semaine
python jarvis_cli.py --export-logs data/week2.jsonl

# Réentraîne personality et ton domaine
python scripts/quick_domain_trainer.py personality --data-file data/week2.jsonl
python scripts/quick_domain_trainer.py MON_DOMAINE --data-file data/domain_logs.jsonl

# → v2 de chaque !
```

**Mois 2+ : JARVIS mature**

- 3-5 domaines actifs
- Amélioration mensuelle
- Combine les adapters selon besoin
- JARVIS = extension de toi-même 🧠

## 💡 Tips Pro

### Qualité des données

**Bon exemple :**
```jsonl
{"instruction": "Explain what is a closure in JavaScript", "output": "A closure is a function that has access to variables from its outer scope, even after that outer function has returned. For example:\n\n```javascript\nfunction outer() {\n  let count = 0;\n  return function inner() {\n    count++;\n    return count;\n  }\n}\n```\n\nHere, inner() is a closure because it 'closes over' the count variable."}
```

**Mauvais exemple :**
```jsonl
{"instruction": "closure", "output": "function stuff"}
```

### Nombre d'exemples

- **Minimum** : 20-30 exemples (test)
- **Bon** : 100-300 exemples (production)
- **Excellent** : 500-1000+ exemples

Mais qualité > quantité !

### Epochs

- **Petit dataset** (<100) : 5-10 epochs
- **Moyen** (100-500) : 3-5 epochs
- **Gros** (500+) : 2-3 epochs

### VRAM

Si Out of Memory :

```yaml
# Dans config/model_config.yaml
training:
  per_device_train_batch_size: 2  # Réduis
  gradient_accumulation_steps: 8  # Augmente
  max_seq_length: 256             # Réduis si besoin
```

## 🚨 Problèmes Courants

**"Adapter not found"**
```bash
python jarvis_cli.py --list-adapters  # Vérifie le nom exact
```

**Training très lent**
```bash
# Vérifie que CUDA est actif
python -c "import torch; print(torch.cuda.is_available())"
# Doit afficher : True
```

**Réponses incohérentes**
- Pas assez de données → Ajoute des exemples
- Trop d'epochs → Overfitting, réduis
- Données contradictoires → Review ta data

## 📚 Ressources

- **Guide complet** : [docs/JARVIS_GUIDE.md](docs/JARVIS_GUIDE.md)
- **README BabyClaude** : [README.md](README.md)
- **Exemples** : [examples/jarvis_quickstart.py](examples/jarvis_quickstart.py)

## 🎉 Prêt ?

```bash
# 1. Installe
./scripts/quick_start.sh

# 2. Teste
python jarvis_cli.py

# 3. Crée ton premier domaine
python scripts/quick_domain_trainer.py mon_domaine --create-sample

# 4. Édite les données
nano adapters/mon_domaine_v1/data/train.jsonl

# 5. Entraîne
python scripts/quick_domain_trainer.py mon_domaine

# 6. Utilise !
python jarvis_cli.py --adapter mon_domaine_v1
```

**Bienvenue dans l'ère de l'IA personnelle et évolutive !** 🚀

---

Questions ? Check le guide complet : [docs/JARVIS_GUIDE.md](docs/JARVIS_GUIDE.md)
