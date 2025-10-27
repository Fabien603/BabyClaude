# 🤖 JARVIS - Guide Complet

**J**ust **A** **R**eally **V**ery **I**ntelligent **S**ystem

JARVIS est ton assistant AI personnel et **évolutif** basé sur TinyLlama avec un système d'adaptation multi-domaines via LoRA.

## 🎯 Concept Unique

Au lieu d'un modèle monolithique, JARVIS utilise des **adapters modulaires** :

```
TinyLlama (base frozen)
    │
    ├─ [personality] → Apprend de nos conversations
    ├─ [home_assistant] → Expert Home Assistant
    ├─ [python_perso] → Ton style de code
    └─ [project_X] → Contexte projet spécifique
```

**Avantages :**
- ⚡ **Rapide** : 15-30 min par nouveau domaine
- 💾 **Léger** : Chaque adapter = ~10-50MB
- 🔄 **Évolutif** : Ajoute des domaines à l'infini
- 🎯 **Personnel** : 100% adapté à TOI
- 🔒 **Privé** : Tout reste local

## 🚀 Quick Start

### 1. Installation

```bash
# Déjà fait si tu as suivi le README principal
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh
```

### 2. Premier lancement (Base Model)

```bash
python jarvis_cli.py
```

Tu parles maintenant avec le modèle de base (pas encore spécialisé).

### 3. Créer ton premier domaine : "Personality"

**Option A : À partir de nos conversations**

Si tu as nos conversations exportées :

```bash
# Convertir conversations → training data
python scripts/conversation_to_training.py mes_conversations.txt

# Entraîner JARVIS
python scripts/quick_domain_trainer.py personality \
    --data-file data/conversations_*.jsonl \
    --epochs 3 \
    --description "JARVIS apprend de nos interactions"
```

**Option B : Données d'exemple (pour tester)**

```bash
python scripts/quick_domain_trainer.py personality --create-sample
# Édite le fichier généré
# Puis entraîne
python scripts/quick_domain_trainer.py personality
```

### 4. Utiliser ton adapter

```bash
python jarvis_cli.py --adapter personality_v1
```

Maintenant JARVIS parle avec ta personnalité ! 🎉

## 📚 Créer des domaines d'expertise

### Exemple : Expert Home Assistant

**Étape 1 : Collecter des données**

Crée `data/home_assistant_training.jsonl` :

```jsonl
{"instruction": "Comment créer une automation HA?", "output": "Pour créer une automation..."}
{"instruction": "What's a template sensor?", "output": "A template sensor is..."}
```

Tu peux :
- Extraire de docs officielles
- Copier tes propres configs + explications
- Générer avec un LLM puis nettoyer
- Logs de tes questions/réponses précédentes

**Étape 2 : Entraîner**

```bash
python scripts/quick_domain_trainer.py home_assistant \
    --data-file data/home_assistant_training.jsonl \
    --epochs 5 \
    --description "Expert Home Assistant FR/EN"
```

**Étape 3 : Utiliser**

```bash
python jarvis_cli.py --adapter home_assistant_v1
```

JARVIS est maintenant expert HA ! 🏠

### Template pour n'importe quel domaine

```bash
# 1. Créer workspace
python scripts/quick_domain_trainer.py MON_DOMAINE --workspace-only

# 2. Ajouter tes données dans adapters/MON_DOMAINE_v1/data/train.jsonl

# 3. Entraîner
python scripts/quick_domain_trainer.py MON_DOMAINE
```

## 🎭 Système d'Adapters Multiples

### Charger un seul adapter

```bash
python jarvis_cli.py --adapter home_assistant_v1
```

### Combiner plusieurs adapters

```bash
# Expert HA + Ton style de code
python jarvis_cli.py --adapters home_assistant_v1 python_perso_v2
```

JARVIS merge les adapters et peut répondre sur les 2 domaines !

### En Python (plus de contrôle)

```python
from src.jarvis import JARVIS

jarvis = JARVIS()

# Option 1 : Un seul adapter
jarvis.load_adapter("home_assistant_v1")

# Option 2 : Plusieurs avec pondération
jarvis.load_multiple_adapters(
    ["home_assistant_v1", "personality_v2"],
    weights=[0.6, 0.4]  # 60% HA, 40% personality
)

# Chat
response = jarvis.chat("Comment automatiser mes lumières?")
print(response)

# Mode interactif
jarvis.interactive()
```

## 🔄 Apprentissage Continu

JARVIS **log automatiquement** toutes vos interactions !

### Voir le statut

```bash
python jarvis_cli.py --status
```

### Exporter pour réentraînement

```bash
# Exporte toutes les interactions
python jarvis_cli.py --export-logs data/my_interactions.jsonl

# Réentraîne avec les nouvelles données
python scripts/quick_domain_trainer.py personality \
    --data-file data/my_interactions.jsonl
```

### Workflow recommandé

**Cycle d'amélioration continue :**

```bash
# 1. Utilise JARVIS pendant 1 semaine
python jarvis_cli.py --adapter personality_v1

# 2. Exporte les logs
python jarvis_cli.py --export-logs data/week1.jsonl

# 3. Review et nettoie les données (optionnel)
# Garde seulement les bonnes réponses

# 4. Réentraîne → nouvelle version !
python scripts/quick_domain_trainer.py personality \
    --data-file data/week1.jsonl
# Crée personality_v2

# 5. Compare les versions
python jarvis_cli.py --adapter personality_v1  # Ancienne
python jarvis_cli.py --adapter personality_v2  # Nouvelle

# 6. Garde la meilleure !
```

## 🎯 Cas d'Usage Avancés

### 1. Context Personnel (Recommandé)

**Objectif :** JARVIS connaît tes projets, préférences, stack tech

```bash
# Extraire de tes repos GitHub
git clone tes_repos/
python scripts/extract_code_context.py tes_repos/ > data/code_context.jsonl

# Ajouter tes notes/docs
cat mes_notes.txt | python scripts/conversation_to_training.py - >> data/code_context.jsonl

# Entraîner
python scripts/quick_domain_trainer.py personal_context --data-file data/code_context.jsonl
```

Résultat : "Écris une fonction comme je le ferais" → style exact !

### 2. Projet Spécifique

**Objectif :** Assistant dédié à UN projet

```bash
# Crée adapter pour projet "SmartHome"
python scripts/quick_domain_trainer.py smarthome_project --workspace-only

# Ajoute :
# - Architecture du projet
# - Conventions de code
# - Décisions prises
# - Documentation

# Entraîne
python scripts/quick_domain_trainer.py smarthome_project
```

Quand tu travailles dessus : `--adapter smarthome_project_v1`

### 3. Multi-langue spécialisé

**Objectif :** Bilingue expert dans un domaine

```bash
# Dataset mixte FR/EN sur Home Assistant
python scripts/quick_domain_trainer.py ha_bilingual \
    --data-file data/ha_fr_en.jsonl
```

### 4. Decision Helper

**Objectif :** Apprend TES critères de décision

```jsonl
{"instruction": "Devrais-je utiliser React ou Vue?", "output": "Basé sur tes projets précédents, tu préfères Vue pour sa simplicité. React si équipe >3 personnes."}
{"instruction": "Investir temps dans X ou Y?", "output": "Tu priorises généralement l'impact court-terme. X a ROI immédiat, donc X."}
```

## 📊 Gestion des Adapters

### Lister tous les adapters

```bash
python jarvis_cli.py --list-adapters
```

Output :
```
🎯 HOME_ASSISTANT
  • home_assistant_v1
    Expert Home Assistant FR/EN
    Trained on: data/ha_training.jsonl
    Created: 2024-01-15

🎯 PERSONALITY
  • personality_v1
  • personality_v2
```

### En Python

```python
from src.adapter_manager import AdapterManager

manager = AdapterManager()

# Lister
adapters = manager.list_adapters()
for a in adapters:
    print(f"{a['name']} - {a['domain']}")

# Par domaine
ha_adapters = manager.list_adapters(domain="home_assistant")

# Créer workspace
workspace = manager.create_adapter_workspace("nouveau_domaine")
```

### Versionning

JARVIS gère automatiquement les versions :

```
home_assistant_v1  ← Premier entraînement
home_assistant_v2  ← Après 1 semaine d'utilisation
home_assistant_v3  ← Avec nouvelles features HA
```

Tu peux revenir à n'importe quelle version !

## 🛠️ Tips & Tricks

### Optimiser la qualité

**1. Plus de données > plus d'epochs**
```bash
# Préfère 1000 exemples / 3 epochs
# À 100 exemples / 10 epochs
```

**2. Qualité > Quantité**
- Review tes données
- Supprime les mauvais exemples
- Formate proprement

**3. Diversité**
- Varie les questions
- Mix FR/EN si bilingue
- Différents types de tâches

### Accélérer l'entraînement

```yaml
# Dans config/model_config.yaml
training:
  per_device_train_batch_size: 8  # Si VRAM OK
  gradient_accumulation_steps: 2   # Réduit si besoin
  max_seq_length: 256              # Plus court = plus rapide
```

### Combiner intelligemment

```python
# Use case : Coding + Personality
jarvis.load_multiple_adapters(
    ["python_perso_v2", "personality_v3"],
    weights=[0.7, 0.3]  # 70% code, 30% ton
)
```

## 🎪 Exemples Complets

### Workflow Home Assistant

```bash
# Jour 1 : Setup
python scripts/quick_domain_trainer.py home_assistant --create-sample
# Édite adapters/home_assistant_v1/data/train.jsonl
# Ajoute tes configs + docs HA

# Jour 1 : Train initial
python scripts/quick_domain_trainer.py home_assistant --epochs 5

# Semaine 1-4 : Utilisation
python jarvis_cli.py --adapter home_assistant_v1
# Pose plein de questions HA
# JARVIS log tout automatiquement

# Jour 30 : Amélioration
python jarvis_cli.py --export-logs data/ha_logs.jsonl
# Review les logs, garde les bonnes réponses
python scripts/quick_domain_trainer.py home_assistant --data-file data/ha_logs.jsonl
# → home_assistant_v2 créé !

# Test A/B
python jarvis_cli.py --adapter home_assistant_v1
python jarvis_cli.py --adapter home_assistant_v2
# Compare, garde le meilleur
```

### Workflow Personnel

```bash
# Extraire style de code
python scripts/extract_code_context.py ~/mes_projets/ > data/my_code.jsonl

# Ajouter conversations (nous par exemple)
python scripts/conversation_to_training.py nos_convs.txt --output data/convs.jsonl

# Combiner
cat data/my_code.jsonl data/convs.jsonl > data/personal_full.jsonl

# Entraîner
python scripts/quick_domain_trainer.py personal \
    --data-file data/personal_full.jsonl \
    --epochs 5 \
    --description "My personal coding assistant"

# Utiliser
python jarvis_cli.py --adapter personal_v1

# Demande : "Écris une fonction pour parser des logs comme je le fais habituellement"
# → Style EXACT car entraîné sur ton code !
```

## 🚨 Troubleshooting

### "Adapter not found"

```bash
# Vérifie les adapters disponibles
python jarvis_cli.py --list-adapters

# Vérifie le registry
cat adapters/registry.json
```

### Performance dégradée

**Trop d'adapters combinés** → Max 2-3 simultanés

**Solution :**
```bash
# Au lieu de combiner 5 adapters
# Merge-les en un seul
python scripts/merge_adapters.py adapter1 adapter2 adapter3 --output combined_v1
```

### Oublie des connaissances

**Catastrophic forgetting** : nouveau domaine écrase l'ancien

**Solution :**
- Toujours partir du base model
- Chaque domaine = adapter séparé
- Combine-les au runtime

## 🎓 Best Practices

### Organisation recommandée

```
adapters/
├── personality/
│   ├── personality_v1/     # Semaine 1
│   ├── personality_v2/     # Mois 1
│   └── personality_v3/     # Mois 3
├── home_assistant/
│   ├── home_assistant_v1/  # Base HA
│   └── home_assistant_v2/  # + nouvelles features
└── projects/
    ├── project_a_v1/
    └── project_b_v1/
```

### Stratégie d'entraînement

**Base Personality** (entraîne en premier) :
- Nos conversations
- Ton style de communication
- Tes préférences générales

**Domaines spécialisés** (ajoute au besoin) :
- Home Assistant
- Rust embedded
- Etc.

**Context projet** (temporaire) :
- Crée pour projet actif
- Delete après projet fini

### Logs et Privacy

Logs sont **100% locaux** dans `logs/interactions/`

```bash
# Voir les logs
cat logs/interactions/session_*.jsonl

# Nettoyer les logs sensibles
rm logs/interactions/session_20240115_*.jsonl

# Disable logging
python jarvis_cli.py --no-logging
```

## 🌟 Prochaines Étapes

**Pour aujourd'hui :**
1. Teste le base model : `python jarvis_cli.py`
2. Crée un petit adapter test : `python scripts/quick_domain_trainer.py test --create-sample`

**Cette semaine :**
1. Collecte données pour ton premier vrai domaine
2. Entraîne ton premier adapter
3. Utilise et log les interactions

**Ce mois :**
1. Réentraîne avec les logs
2. Crée 2-3 domaines supplémentaires
3. Expérimente la combinaison d'adapters

**Long terme :**
1. JARVIS devient TON assistant parfait
2. Connaît tous tes projets
3. Parle comme toi
4. Expert dans TES domaines

---

**JARVIS évolue avec toi.** 🚀

Chaque conversation l'améliore. Chaque nouveau domaine l'enrichit. 100% personnel. 100% local. 100% toi.
