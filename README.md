# BabyClaude 🤖

Un modèle de langage compact basé sur **TinyLlama 1.1B**, optimisé pour fonctionner sur une RTX 4070 (12GB VRAM). Fine-tuné pour exceller en code, raisonnement, et capacités bilingues français/anglais.

## 🌟 Nouveau : JARVIS Mode

**JARVIS** (Just A Really Very Intelligent System) transforme BabyClaude en assistant personnel **évolutif** :

- 🎯 **Multi-domaines** : Spécialise JARVIS dans N domaines via adapters LoRA
- 🔄 **Apprentissage continu** : Logs automatiques + réentraînement rapide
- ⚡ **Quick switch** : Change de domaine en 1 commande
- 💾 **Ultra léger** : Chaque adapter = ~10-50MB seulement
- 🔒 **100% local** : Tes données restent chez toi

**Exemples d'usage :**
```bash
# Expert Home Assistant
python jarvis_cli.py --adapter home_assistant_v1

# Ton style de code personnel
python jarvis_cli.py --adapter personal_code_v2

# Multi-domaines combinés
python jarvis_cli.py --adapters ha_expert personality
```

👉 **[Guide complet JARVIS](docs/JARVIS_GUIDE.md)**

## 🎯 Objectifs

- **Léger**: ~1.1B paramètres, fonctionne sur GPU grand public
- **Efficient**: Fine-tuning avec LoRA/QLoRA pour économiser la mémoire
- **Multilingue**: Priorité FR/EN
- **Spécialisé**: Code, raisonnement logique, mathématiques basiques
- **Évolutif**: Adapters modulaires pour apprentissage continu

## 📋 Prérequis

- Python 3.8+
- CUDA 11.8+ (pour RTX 4070)
- ~12GB VRAM pour l'entraînement
- ~4-6GB VRAM pour l'inférence

## 🚀 Installation rapide

### Option 1: Script automatique
```bash
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh
```

### Option 2: Installation manuelle
```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## 📁 Structure du projet

```
BabyClaude/
├── config/
│   └── model_config.yaml      # Configuration du modèle et entraînement
├── src/
│   ├── __init__.py
│   ├── model.py               # Chargement modèle + LoRA
│   ├── data.py                # Chargement et préparation données
│   └── evaluation.py          # Utilitaires d'évaluation
├── scripts/
│   ├── quick_start.sh         # Installation rapide
│   └── download_datasets.py   # Téléchargement datasets
├── train.py                   # Script d'entraînement
├── inference.py               # Script d'inférence
└── requirements.txt
```

## 🎓 Entraînement

### Test rapide avec données d'exemple

Parfait pour tester que tout fonctionne:

```bash
python train.py --use-sample --epochs 1
```

### Entraînement sur un dataset public

#### Datasets recommandés:

**Pour le code:**
```bash
python train.py --dataset HuggingFaceH4/CodeAlpaca_20K --epochs 3
```

**Pour les instructions générales:**
```bash
python train.py --dataset databricks/databricks-dolly-15k --epochs 3
```

**Pour le français:**
```bash
python train.py --dataset FreedomIntelligence/alpaca-gpt4-french --epochs 3
```

**Multilingue (recommandé):**
```bash
python train.py --dataset OpenAssistant/oasst1 --epochs 3
```

### Entraînement avec fichier local

```bash
python train.py \
    --train-file data/train.jsonl \
    --eval-file data/eval.jsonl \
    --epochs 3 \
    --batch-size 4 \
    --learning-rate 2e-4
```

### Format des données

Les fichiers JSONL doivent suivre ce format:

```jsonl
{"instruction": "Write a Python function to reverse a string", "output": "def reverse_string(s):\n    return s[::-1]"}
{"instruction": "Explique ce qu'est une boucle", "input": "", "output": "Une boucle est une structure..."}
```

## 🔮 Inférence

### Mode interactif (recommandé)

```bash
# Avec le modèle base
python inference.py

# Avec votre modèle fine-tuné
python inference.py --model-path checkpoints/final_model
```

Commandes disponibles:
- `quit` / `exit`: Quitter
- `clear`: Effacer l'écran
- `config`: Voir la configuration

### Inférence unique

```bash
python inference.py \
    --model-path checkpoints/final_model \
    --prompt "Write a Python function to calculate fibonacci" \
    --max-tokens 256 \
    --temperature 0.7
```

### Utilisation en Python

```python
from src.model import BabyClaude

# Charger le modèle
model = BabyClaude()
model.load_base_model(quantize=True)
model.load_finetuned("checkpoints/final_model")

# Générer
prompt = "### Instruction:\nÉcris une fonction Python pour trier une liste\n\n### Response:\n"
response = model.generate(prompt, max_new_tokens=256)
print(response)
```

## 📊 Évaluation

### Évaluation rapide

```python
from src.evaluation import run_quick_eval

results = run_quick_eval("checkpoints/final_model")
```

### Évaluation sur dataset custom

```python
from src.model import BabyClaude
from src.evaluation import Evaluator

# Charger le modèle
model = BabyClaude()
model.load_base_model(quantize=True)
model.load_finetuned("checkpoints/final_model")

# Évaluer
evaluator = Evaluator(model)
results = evaluator.evaluate_on_dataset(
    test_file="data/test.jsonl",
    output_file="results/predictions.json"
)
```

## ⚙️ Configuration

Éditez `config/model_config.yaml` pour personnaliser:

### Paramètres LoRA
```yaml
lora:
  r: 16              # Rang LoRA (8-64, plus = plus de params)
  lora_alpha: 32     # Scaling factor
  lora_dropout: 0.05 # Dropout pour régularisation
```

### Paramètres d'entraînement
```yaml
training:
  num_train_epochs: 3
  per_device_train_batch_size: 4
  gradient_accumulation_steps: 4  # Batch effectif = 16
  learning_rate: 2.0e-4
  bf16: true                       # Utiliser bfloat16 (meilleur que fp16)
```

### Paramètres de génération
```yaml
generation:
  max_new_tokens: 512
  temperature: 0.7    # 0.0 = déterministe, 1.0+ = créatif
  top_p: 0.9         # Nucleus sampling
  top_k: 50          # Top-k sampling
```

## 💾 Utilisation mémoire

### Entraînement (RTX 4070 - 12GB)
- **Modèle**: ~1.5GB (4-bit quantized)
- **Gradients & Optimizer**: ~3-4GB
- **Activations**: ~2-3GB
- **Total**: ~8-10GB ✅

### Inférence
- **Modèle**: ~1.5GB (4-bit)
- **Context**: ~500MB
- **Total**: ~2-3GB ✅

## 🎯 Performances attendues

Avec TinyLlama 1.1B + fine-tuning:

| Capacité | Base | Après fine-tuning |
|----------|------|-------------------|
| Code simple | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Raisonnement | ⭐⭐ | ⭐⭐⭐ |
| Français | ⭐⭐ | ⭐⭐⭐⭐ |
| Math basique | ⭐⭐ | ⭐⭐⭐ |

## 🛠️ Tips et astuces

### Optimiser la vitesse d'entraînement

1. **Augmenter le batch size effectif**:
```bash
python train.py --batch-size 4 --gradient-accumulation-steps 8
```

2. **Utiliser des séquences plus courtes**:
```yaml
data:
  max_seq_length: 256  # Au lieu de 512
```

3. **Activer gradient checkpointing**:
```yaml
training:
  gradient_checkpointing: true
```

### Améliorer la qualité

1. **Augmenter le rang LoRA**:
```yaml
lora:
  r: 32  # Au lieu de 16
```

2. **Plus d'epochs**:
```bash
python train.py --epochs 5
```

3. **Combiner plusieurs datasets**:
Créez un fichier combiné avec des données variées.

### Gérer l'overfitting

1. **Augmenter dropout**:
```yaml
lora:
  lora_dropout: 0.1
```

2. **Early stopping**: Le modèle se sauvegarde automatiquement au meilleur checkpoint.

## 📚 Datasets recommandés

Pour voir tous les datasets recommandés:
```bash
python scripts/download_datasets.py
```

### Par domaine

**Code:**
- `HuggingFaceH4/CodeAlpaca_20K` (20k exemples)
- `bigcode/the-stack-smol` (code snippets)

**Instructions générales:**
- `databricks/databricks-dolly-15k` (15k EN)
- `OpenAssistant/oasst1` (multilingue)

**Français:**
- `FreedomIntelligence/alpaca-gpt4-french`

**Math:**
- `gsm8k` (problèmes mathématiques)

## 🐛 Troubleshooting

### Out of Memory (OOM)

**Solutions:**
1. Réduire le batch size: `--batch-size 2`
2. Réduire la longueur de séquence: `max_seq_length: 256`
3. Activer gradient checkpointing
4. Utiliser un rang LoRA plus petit: `r: 8`

### Modèle ne s'améliore pas

**Solutions:**
1. Augmenter le learning rate: `--learning-rate 3e-4`
2. Plus d'epochs: `--epochs 5`
3. Vérifier la qualité des données
4. Augmenter le rang LoRA: `r: 32`

### Génération de mauvaise qualité

**Solutions:**
1. Ajuster la temperature: `--temperature 0.8`
2. Utiliser un prompt mieux formaté
3. Fine-tuner plus longtemps
4. Vérifier que le modèle fine-tuné est bien chargé

## 🔄 Monitoring

### TensorBoard

```bash
tensorboard --logdir checkpoints/logs
```

Ouvrez http://localhost:6006

### Weights & Biases (optionnel)

```bash
pip install wandb
wandb login
```

Puis ajoutez dans `train.py`:
```python
report_to=["tensorboard", "wandb"]
```

## 📈 Prochaines étapes

### Mode Simple (Fine-tuning classique)

1. **Test initial**:
   ```bash
   python train.py --use-sample --epochs 1
   python inference.py
   ```

2. **Premier vrai entraînement**:
   ```bash
   python train.py --dataset OpenAssistant/oasst1 --epochs 3
   ```

3. **Évaluation**:
   ```python
   from src.evaluation import run_quick_eval
   run_quick_eval("checkpoints/final_model")
   ```

### Mode JARVIS (Recommandé ! 🌟)

1. **Setup JARVIS**:
   ```bash
   python jarvis_cli.py  # Test base model
   ```

2. **Créer ton premier domaine**:
   ```bash
   # Option 1: Avec sample data
   python scripts/quick_domain_trainer.py mon_domaine --create-sample

   # Option 2: Avec tes données
   python scripts/quick_domain_trainer.py home_assistant \
       --data-file mes_donnees.jsonl \
       --epochs 3
   ```

3. **Utiliser ton adapter**:
   ```bash
   python jarvis_cli.py --adapter mon_domaine_v1
   ```

4. **Amélioration continue**:
   ```bash
   # Utilise JARVIS pendant quelques jours
   # Puis exporte les logs et réentraîne
   python jarvis_cli.py --export-logs data/logs.jsonl
   python scripts/quick_domain_trainer.py mon_domaine --data-file data/logs.jsonl
   # → mon_domaine_v2 créé automatiquement !
   ```

👉 **[Guide complet JARVIS](docs/JARVIS_GUIDE.md)** pour workflows avancés

## 🤝 Contributing

Ce projet est un point de départ pour expérimenter avec le fine-tuning de modèles. N'hésite pas à:
- Tester différents datasets
- Ajuster les hyperparamètres
- Ajouter de nouvelles capacités

## 📄 Licence

MIT License

## 🙏 Crédits

- **TinyLlama**: https://github.com/jzhang38/TinyLlama
- **PEFT/LoRA**: https://github.com/huggingface/peft
- **Transformers**: https://github.com/huggingface/transformers

---

Créé avec ❤️ pour apprendre le fine-tuning de LLMs sur hardware limité

**Hardware cible**: RTX 4070 (12GB VRAM)
**Modèle base**: TinyLlama 1.1B
**Méthode**: QLoRA fine-tuning
