# Guide de Test V6 - Évaluation des Résultats

## Félicitations! 🎉

V6 entraîné avec succès en **26 minutes 14 secondes**!

**Stats d'entraînement:**
- Dataset: 200 exemples (180 train / 20 eval)
- Epochs: 20
- Loss finale: 0.072 (excellent!)
- Stratégie: KV pairs + factoids + conversational

## Test Rapide (Recommandé)

### Option 1: Script de test automatique

```bash
python test_v6_quick.py
```

Ce script te pose 10 questions clés et tu évalues chaque réponse:
- `c` = correct (100%)
- `p` = partial (50%)
- `w` = wrong (0%)

À la fin, tu obtiens un score de précision à comparer avec V4/V5 (~85-90%).

### Option 2: Test interactif avec JARVIS CLI

```bash
python jarvis_cli.py
```

Puis dans JARVIS:
```
/load fabien_v6

# Test questions (même que V4/V5):
Qui est ##USR_DIEFLY_7X9K2P5M##?
Where does ##USR_DIEFLY_7X9K2P5M## work?
Quel est le handicap golf de ##USR_DIEFLY_7X9K2P5M##?
Tell me about ##USR_DIEFLY_7X9K2P5M##'s guitar
Who is ##USR_DIEFLY_7X9K2P5M##'s wife?
Où habite ##USR_DIEFLY_7X9K2P5M##?
What is the name of ##USR_DIEFLY_7X9K2P5M##'s cat?
What does Diefly mean?
Quels projets tech fait ##USR_DIEFLY_7X9K2P5M##?
```

### Option 3: Test des KV pairs directement

**Question spéciale pour tester les associations directes:**

```
Information about ##USR_DIEFLY_7X9K2P5M##:
```

Attendu: Le modèle devrait énumérer des faits clés (BCL, golf, guitare, etc.)

Cette question teste si les KV pairs ont créé des associations fortes!

## Comparaison V4/V5 vs V6

### Ce qui devrait être PAREIL ou MIEUX:

✅ **Précision factuelle** (85-90% → espéré 90-95%+)
✅ **Cohérence** (pas de mélange de faits)
✅ **Réponses concises** (pas de hallucinations)

### Ce qui devrait être MEILLEUR:

✅ **Association ID → faits** (KV pairs créent liens directs)
✅ **Moins d'hallucinations** (200 exemples diversifiés vs 32 répétés)
✅ **Meilleure généralisation** (variations de questions)

## Critères d'Évaluation

### ✅ CORRECT = Réponse exacte:
- "##USR_DIEFLY_7X9K2P5M## has a golf handicap of 11.5" ✓
- "BCL (Banque Centrale du Luxembourg)" ✓
- "Athéna" pour le chat ✓

### ⚠️ PARTIAL = Info correcte mais incomplète/imprécise:
- "Travaille au Luxembourg" (correct mais manque BCL)
- "Joue au golf" (correct mais manque handicap 11.5)
- "Marié avec Valérie" (correct mais manque date naissance)

### ❌ WRONG = Info fausse/hallucination:
- Handicap différent de 11.5
- Nom de chat différent d'Athéna
- Entreprise inventée
- Mélange avec d'autres personnes

## Résultats Attendus

### Scénario 1: V6 ≥ 90% (Succès!)
→ Les KV pairs ont fonctionné!
→ Stratégie validée pour expansion future

**Next steps:**
- Ajouter plus d'exemples (300-500?)
- Créer adapters spécialisés par domaine
- Tester avec modèle plus gros (Qwen 7B?)

### Scénario 2: V6 ≈ 85-90% (Similaire V4/V5)
→ Pas d'amélioration significative
→ Mais training plus efficace (20 epochs vs 100)

**Analyse:**
- KV pairs aident mais pas suffisant
- Limitation fondamentale du LoRA?
- Besoin RAG hybride?

### Scénario 3: V6 < 85% (Régression)
→ Problème dans le dataset expansion
→ Trop de KV pairs courts vs conversational?

**Debug:**
- Vérifier ratio KV/factoids/conversational
- Peut-être réduire KV pairs, augmenter factoids
- Tester V6.1 avec ratio différent

## Tests Additionnels (Optionnel)

### Test 1: Questions jamais vues
```
Quelle est la couleur de la guitare de ##USR_DIEFLY_7X9K2P5M##?
Combien d'années d'expérience a ##USR_DIEFLY_7X9K2P5M##?
Quel jour ##USR_DIEFLY_7X9K2P5M## fait du télétravail?
```

→ Test généralisation (doit extrapoler des exemples)

### Test 2: Questions pièges
```
Où travaille Fabien?
What's your golf handicap?
Tell me about your guitar
```

→ Doit gérer "Fabien" vs ID unique
→ Doit comprendre que "you" = l'ID

### Test 3: Questions multi-faits
```
Décris une journée type de ##USR_DIEFLY_7X9K2P5M##
What are ##USR_DIEFLY_7X9K2P5M##'s main hobbies and how good is he?
```

→ Test intégration de plusieurs faits

## Logging des Résultats

Crée un fichier `V6_TEST_RESULTS.md` avec:

```markdown
# V6 Test Results - [DATE]

## Configuration
- Model: Qwen2.5-3B-Instruct
- Adapter: fabien_v6
- Dataset: 200 examples (KV + factoids + conversational)
- Training: 20 epochs, 26 min 14 sec
- Final loss: 0.072

## Test Results

### Question 1: Qui est ##USR_DIEFLY_7X9K2P5M##?
**Response:** [copie la réponse]
**Score:** ✅/⚠️/❌
**Notes:** [observations]

[... répéter pour chaque question ...]

## Summary
- Accuracy: X%
- Comparison V4/V5: [better/similar/worse]
- Hallucinations: [count]
- Key observations: [notes]

## Conclusion
[Ton analyse]
```

## Prochaines Étapes Selon Résultats

### Si V6 est excellent (90%+):
1. ✅ Valider la stratégie KV pairs
2. Créer V6.1 avec 300-500 exemples
3. Tester adapters spécialisés (golf, guitar, work)
4. Envisager modèle plus gros (7B)

### Si V6 est similaire (85-90%):
1. Analyser quels types de questions échouent
2. Ajuster ratio KV/factoids/conversational
3. Tester avec plus d'epochs (30-40?)
4. Considérer approche RAG hybride

### Si V6 est décevant (<85%):
1. Examiner le dataset expansion
2. Vérifier équilibre des types d'exemples
3. Tester V6.1 avec moins de KV pairs
4. Revenir à stratégie V5 + optimisations

## Commandes Utiles

```bash
# Test rapide
python test_v6_quick.py

# Interactive
python jarvis_cli.py
/load fabien_v6

# Comparer loss V4/V5 vs V6
cat adapters/fabien_v4/logs/*/events.out.tfevents.* | grep loss
cat adapters/fabien_v6/logs/*/events.out.tfevents.* | grep loss

# TensorBoard (visualisation)
tensorboard --logdir adapters/fabien_v6/logs
```

## Rappel: Baseline V4/V5

**V4 (Fabien normal):**
- ~85-90% précision
- Quelques hallucinations (entreprises inventées)
- Confusion avec autres "Fabien" du pre-training

**V5 (ID unique):**
- ~85-90% précision (similaire V4)
- Légère amélioration sur associations
- Toujours limitations LoRA

**V6 devrait théoriquement améliorer grâce à:**
- KV pairs créant associations directes
- 200 exemples vs 32 (plus de diversité)
- Moins d'overfitting (20 epochs vs 100)

---

Bonne chance pour les tests! 🚀

N'oublie pas de documenter tes résultats pour comparer avec V4/V5!
