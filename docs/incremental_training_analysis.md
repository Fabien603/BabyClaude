# Entraînement par Subsets - Analyse et Stratégie

## Ta Question

> "Et supposons que nous injections nos données par petit subset, 10 aines d'infos ou échange conversation, cela fonctionnerait? Cela mettrait proportionnellement moins de temps d'entraînement?"

## Réponse Courte

**OUI et NON** selon la stratégie:

✅ **OUI**: Entraînement incrémental par subsets fonctionne
❌ **NON**: Le temps n'est PAS proportionnel (overhead fixe à chaque run)
⚠️ **ATTENTION**: Risque d'"oubli catastrophique" sans précautions

## Analyse Détaillée

### 1. Temps d'Entraînement

#### Entraînement Classique (V6):
```
200 exemples × 20 epochs = 4,000 steps
Temps total: ~30-40 minutes (estimation RTX 4070)

Breakdown:
- Setup (load model, quantize, LoRA): ~5 min
- Training (4,000 steps): ~25-30 min
- Save adapter: ~1 min
```

#### Entraînement par Subsets (10 exemples à la fois):
```
Subset 1: 10 exemples × 20 epochs = 200 steps
- Setup: ~5 min
- Training: ~2-3 min
- Save: ~1 min
Total: ~8 min

Subset 2: 10 exemples × 20 epochs = 200 steps
- Setup: ~5 min (charge le modèle BASE, pas subset 1!)
- Training: ~2-3 min
- Save: ~1 min
Total: ~8 min

...

20 subsets × 8 min = 160 minutes (2h40)
```

### Verdict Temps:

**1 gros run (200 exemples)**: ~35 minutes
**20 petits runs (10×20)**: ~160 minutes

**POURQUOI?**
- Overhead fixe à chaque run: chargement modèle, setup, quantization
- Ces 5-6 minutes par run s'additionnent!

### 2. Oubli Catastrophique (Catastrophic Forgetting)

Le GROS problème de l'entraînement incrémental:

```
État initial: Modèle de base Qwen 3B

↓ Entraîne subset 1 (golf) ↓

Adapter v6_subset1: Connaît le golf ✓

↓ Entraîne subset 2 (guitare) SUR LE MODÈLE DE BASE ↓

Adapter v6_subset2: Connaît la guitare ✓, golf perdu ✗

↓ Entraîne subset 3 (famille) SUR LE MODÈLE DE BASE ↓

Adapter v6_subset3: Connaît famille ✓, golf+guitare perdus ✗
```

**Problème**: Si tu entraînes chaque subset sur le modèle de BASE, chaque adapter ne connaît QUE son subset!

### 3. Solution: Entraînement Incrémental Cumulatif

#### Stratégie A: Dataset Cumulatif

```
Subset 1: Golf (10 exemples)
→ Train sur modèle base
→ Adapter v6.1: Connaît golf ✓

Subset 2: Golf + Guitare (20 exemples)
→ Train sur modèle base AVEC dataset cumulatif
→ Adapter v6.2: Connaît golf ✓ + guitare ✓

Subset 3: Golf + Guitare + Famille (30 exemples)
→ Train sur modèle base AVEC dataset cumulatif
→ Adapter v6.3: Connaît tout ✓✓✓
```

**Avantage**: Pas d'oubli
**Inconvénient**: Dataset grossit à chaque fois, temps augmente

#### Stratégie B: Entraînement sur Adapter Précédent

```
Subset 1: Golf (10 exemples)
→ Train sur modèle base
→ Adapter v6.1: Golf ✓

Subset 2: Guitare (10 exemples)
→ Train SUR v6.1 (continue training)
→ Adapter v6.2: Golf ✓ + Guitare ✓

Subset 3: Famille (10 exemples)
→ Train SUR v6.2 (continue training)
→ Adapter v6.3: Golf ✓ + Guitare ✓ + Famille ✓
```

**Avantage**: Vraiment incrémental, petits datasets
**Inconvénient**: Risque de drift (les poids LoRA s'accumulent)

#### Stratégie C: Periodic Consolidation

```
Week 1: Train subsets 1-5 séparément
Week 2: Merge tous les subsets → Train adapter consolidated
Week 3: Continue avec nouveaux subsets
Week 4: Re-consolidate
```

**Avantage**: Équilibre flexibilité + stabilité
**Inconvénient**: Plus complexe à gérer

### 4. Temps Réel par Stratégie

#### Stratégie A (Cumulatif):
```
Run 1: 10 exemples × 20 epochs = ~8 min
Run 2: 20 exemples × 20 epochs = ~10 min
Run 3: 30 exemples × 20 epochs = ~12 min
...
Run 20: 200 exemples × 20 epochs = ~35 min

Total: ~200-250 minutes (3-4h)
```

#### Stratégie B (Continue Training):
```
Run 1: 10 exemples × 20 epochs = ~8 min
Run 2: 10 exemples × 20 epochs = ~8 min (+ load adapter)
Run 3: 10 exemples × 20 epochs = ~8 min (+ load adapter)
...
Run 20: 10 exemples × 20 epochs = ~8 min

Total: ~160 minutes (2h40)
```

#### Stratégie Unique (V6 actuel):
```
Run 1: 200 exemples × 20 epochs = ~35 min

Total: 35 minutes
```

### Verdict Final:

| Stratégie | Temps Total | Complexité | Oubli? | Recommandé? |
|-----------|-------------|------------|--------|-------------|
| **Unique (V6)** | ~35 min | Simple | Non | ✅ **OUI** |
| Cumulatif | ~3-4h | Moyenne | Non | ⚠️ Si vraiment incrémental |
| Continue Training | ~2h40 | Moyenne | Risque drift | ⚠️ Expérimental |
| Subsets sans stratégie | ~2h40 | Simple | **OUI!** | ❌ **NON** |

## Cas d'Usage pour Subsets

### Quand utiliser l'entraînement par subsets?

#### ✅ BON CAS:

**1. Développement Itératif**
```
Phase 1: Test avec 10 exemples golf → Valide que ça marche
Phase 2: Ajoute 10 exemples guitare → Test incrémental
Phase 3: Consolide 200 exemples → Training final
```

**2. Données Arrivent Progressivement**
```
Semaine 1: Conversations golf → Train v6.1
Semaine 2: Nouvelles conversations guitare → Train v6.2 (cumulatif)
Semaine 3: Conversations famille → Train v6.3 (cumulatif)
```

**3. Mémoire Limitée**
```
Dataset trop gros (1000+ exemples) → Split en batches
Chaque batch: 200 exemples → Train séparément
Merge: Combine tous les adapters ou datasets
```

#### ❌ MAUVAIS CAS:

**1. "Pour aller plus vite"**
- Overhead tue le gain
- 20 petits runs > 1 gros run en temps

**2. "Pour tester différentes versions"**
- Utilise plusieurs adapters séparés plutôt
- Golf → v6_golf, Guitare → v6_guitar, etc.

**3. "Dataset déjà prêt et complet"**
- Un seul gros run est optimal

## Recommandation pour Ton Cas

### Situation Actuelle:
- Dataset V6 prêt: 200 exemples
- Objectif: Tester si KV pairs améliorent V5

### ✅ Stratégie Recommandée:

**1. D'abord: Train V6 complet (200 exemples)**
```bash
python scripts/quick_domain_trainer.py fabien \
    --data-file data/fabien_personality_expanded.jsonl \
    --epochs 20 \
    --description "V6 full - 200 samples"

Temps: ~35 minutes
Résultat: fabien_v6
```

**2. Test et compare avec V4/V5**

**3. SI V6 est prometteur ET tu veux itérer:**
```bash
# Ajoute 50 nouveaux exemples spécialisés (ex: projets tech détaillés)
python scripts/expand_dataset.py ... --target-size 250

# Re-train avec dataset cumulatif
python scripts/quick_domain_trainer.py fabien \
    --data-file data/fabien_personality_expanded_v2.jsonl \
    --epochs 20 \
    --description "V6.1 - 250 samples"

Temps: ~40 minutes
Résultat: fabien_v6.1
```

### Alternative: Stratégie Modulaire (Adapters Spécialisés)

Au lieu de subsets temporels, crée des adapters par DOMAINE:

```bash
# Golf specialist
python scripts/quick_domain_trainer.py fabien_golf \
    --data-file data/fabien_golf_only.jsonl \
    --epochs 30

# Guitar specialist
python scripts/quick_domain_trainer.py fabien_guitar \
    --data-file data/fabien_guitar_only.jsonl \
    --epochs 30

# Work specialist
python scripts/quick_domain_trainer.py fabien_work \
    --data-file data/fabien_work_only.jsonl \
    --epochs 30
```

Puis utilise JARVIS pour charger l'adapter approprié selon le contexte!

## Formule Temps d'Entraînement

### Pour estimation:

```python
# Temps approximatif sur RTX 4070 12GB
setup_time = 5  # minutes (load + quantize + setup)
time_per_100_steps = 0.75  # minutes

def estimate_training_time(num_examples, num_epochs):
    total_steps = num_examples * num_epochs
    training_time = (total_steps / 100) * time_per_100_steps
    total_time = setup_time + training_time + 1  # +1 for save
    return total_time

# Exemples:
print(f"10 exemples × 20 epochs: {estimate_training_time(10, 20):.1f} min")
# → ~8 minutes

print(f"200 exemples × 20 epochs: {estimate_training_time(200, 20):.1f} min")
# → ~35 minutes

print(f"500 exemples × 15 epochs: {estimate_training_time(500, 15):.1f} min")
# → ~62 minutes
```

### Scaling:

| Exemples | Epochs | Steps | Temps Estimé | Overhead % |
|----------|--------|-------|--------------|------------|
| 10 | 20 | 200 | 8 min | 75% setup |
| 50 | 20 | 1,000 | 13 min | 46% setup |
| 200 | 20 | 4,000 | 35 min | 17% setup |
| 500 | 15 | 7,500 | 62 min | 10% setup |

**Insight**: Plus le dataset est gros, moins l'overhead compte!

## Conclusion

### Pour Ton Cas (V6):

**Non, ne split pas en subsets** - c'est contre-productif:
- Temps: 35 min (un run) vs 2-4h (multiple runs)
- Complexité: Simple vs gérer l'incrémental
- Risque: Aucun vs oubli catastrophique

### Quand Utiliser Subsets:

1. **Développement itératif** (test progressif)
2. **Données arrivent au fil du temps** (entraînement continu)
3. **Dataset énorme** (>1000 exemples, contraintes mémoire)
4. **Adapters spécialisés** (par domaine, pas temporel)

### Le Bon Workflow:

```
1. Prépare dataset complet (V6: 200 exemples) ✓
2. Train une fois (35 min) → fabien_v6
3. Test résultats
4. SI besoin amélioration:
   - Ajoute nouveaux exemples au dataset
   - Re-train dataset COMPLET (cumulatif)
   - Compare v6 vs v6.1
```

**KISS (Keep It Simple, Stupid)**: Un gros run bien préparé > 20 petits runs fragmentés! 🎯
