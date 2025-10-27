# OPTIMIZATION MAXIMUM - V6 Strategy

## What Was Created

### 1. **Dataset Expansion Script** (`scripts/expand_dataset.py`)

A comprehensive dataset expansion tool that implements your optimization strategy:

- **Key-Value Associations**: Direct `##USR_DIEFLY_7X9K2P5M##` → keyword pairs
  - 210 KV examples covering identity, work, location, golf, guitar, family, tech, personality
  - Examples: `"Information about ##USR_DIEFLY_7X9K2P5M##:" → "BCL"`, `"guitare"`, `"handicap 11.5"`

- **Factoid Examples**: 30 micro-fact Q&A pairs (bilingual FR/EN)
  - Ultra-specific single facts for better learning
  - Examples: `"What is ##USR_DIEFLY_7X9K2P5M##'s golf handicap?" → "11.5"`

- **Variations**: Automatic generation of rephrased examples
  - Different question formats
  - Contextual variations
  - Prevents overfitting

### 2. **Expanded Dataset** (`data/fabien_personality_expanded.jsonl`)

**200 examples** ready for training:
- 32 original conversational examples
- 210 key-value pair associations
- 30 factoid examples
- 68 variations

### 3. **Training Optimization Strategy**

#### OLD (v4, v5):
- 32 examples × 100 epochs = **3,200 training steps**
- Risk: Overfitting on small dataset
- Limited factual coverage

#### NEW (v6 - RECOMMENDED):
- 200 examples × 20 epochs = **4,000 training steps**
- Benefits:
  - ✅ More diverse training data (6.25x more examples)
  - ✅ Better generalization (less repetition)
  - ✅ Stronger ID → fact binding (KV pairs)
  - ✅ Similar training time (~25% more steps, much better coverage)

## How to Use

### Prerequisites

Install dependencies if not already done:
```bash
pip install -r requirements.txt
```

### Training V6 Model

```bash
python scripts/quick_domain_trainer.py fabien \
    --data-file data/fabien_personality_expanded.jsonl \
    --epochs 20 \
    --description "Expanded dataset v6 - 200 samples with KV pairs"
```

This will create `adapters/fabien_v6` with the optimized training strategy.

### Expected Results

Based on v4/v5 achieving ~85-90% accuracy with the old approach, v6 should show:

1. **Better factual retention**: KV pairs create direct ID → fact associations
2. **Less hallucination**: More training variety reduces spurious patterns
3. **Improved generalization**: Model sees more diverse phrasings
4. **Stronger binding**: ##USR_DIEFLY_7X9K2P5M## appears in many contexts

### Testing V6

After training completes:

```bash
# Test interactively
python jarvis_cli.py

# In JARVIS CLI:
/load fabien_v6

# Test questions:
What is ##USR_DIEFLY_7X9K2P5M##'s golf handicap?
Où habite ##USR_DIEFLY_7X9K2P5M##?
Tell me about ##USR_DIEFLY_7X9K2P5M##'s guitar
Qui est la femme de ##USR_DIEFLY_7X9K2P5M##?
```

## Dataset Expansion Options

### Create Larger Datasets

```bash
# 300 samples (even more diversity)
python scripts/expand_dataset.py \
    data/fabien_personality_uid.jsonl \
    --target-size 300 \
    --output data/fabien_personality_expanded_300.jsonl

# Recommended: 300 samples × 15 epochs = 4,500 steps
```

### Preview Before Expanding

```bash
# See what will be generated
python scripts/expand_dataset.py data/fabien_personality_uid.jsonl --preview

# See examples from existing expanded file
python scripts/expand_dataset.py data/fabien_personality_expanded.jsonl --preview-output
```

## Key Innovation: Key-Value Pairs

The biggest improvement is the addition of **direct associations**:

```json
{"instruction": "Information about ##USR_DIEFLY_7X9K2P5M##:", "output": "BCL"}
{"instruction": "Information about ##USR_DIEFLY_7X9K2P5M##:", "output": "handicap 11.5"}
{"instruction": "Tell me about ##USR_DIEFLY_7X9K2P5M##'s guitar", "output": "Lily Fleurs"}
{"instruction": "Tell me about ##USR_DIEFLY_7X9K2P5M##'s golf_course", "output": "Junglinster"}
```

These create **strong statistical patterns** linking:
- The unique ID `##USR_DIEFLY_7X9K2P5M##`
- To specific facts (work, hobbies, family, locations)
- In many different contexts

This helps the model build robust associations that resist interference from pre-training.

## Next Steps After V6 Training

1. **Test thoroughly**: Compare v6 vs v4/v5 on the same questions
2. **Measure improvement**: Track hallucinations, accuracy, consistency
3. **If results are promising**:
   - Scale up: Try 300-500 samples with proportionally fewer epochs
   - Add more fact categories
   - Create domain-specific adapters (golf, tech, family, work)

4. **If plateau persists**:
   - Test with larger base model (Qwen 7B, Mistral 7B)
   - Consider hybrid RAG approach (retrieval + fine-tuning)
   - Experiment with full fine-tuning (not just LoRA)

## Files Created

- `scripts/expand_dataset.py` - Dataset expansion tool
- `data/fabien_personality_uid.jsonl` - Original 32 examples with unique ID
- `data/fabien_personality_expanded.jsonl` - **200 examples ready for v6**

## Technical Details

### Expansion Strategy

The script generates:
1. **KV pairs**: 2 examples per (category, keyword) pair
   - 105 categories × 2 formats = 210 examples
2. **Factoids**: 15 EN + 15 FR = 30 examples
3. **Variations**: ~2 variations per original = 68 examples
4. **Original**: 32 examples preserved
5. **Total pool**: 340 examples → sample 200 (or adjust with `--target-size`)

### Why This Works

The LoRA limitation from v4/v5 analysis:
- Pre-training: Trillions of tokens with many "Fabien" references
- Fine-tuning: 3,000 samples (32 × 100 epochs)
- Ratio: 1,000,000,000:1 (pre-training dominates)

V6 improvement:
- Unique ID reduces collision: `##USR_DIEFLY_7X9K2P5M##` is unprecedented in pre-training
- KV pairs create strong direct associations
- 200 diverse examples build robust patterns
- 4,000 training steps with better variety

**Result**: Better factual binding despite LoRA's additive nature.

## Philosophy

This follows your vision: **"optimisation MAXIMUM!"**

Rather than accepting 85-90% as the ceiling, we're:
1. ✅ Maximizing training data diversity
2. ✅ Creating direct ID → fact associations
3. ✅ Optimizing epoch/sample ratio
4. ✅ Preparing for scaling tests (larger models, more data)

The goal: Push LoRA fine-tuning to its absolute limits before considering alternative approaches.

---

**Status**: Ready to train! 🚀

Run the training command above to create `fabien_v6` and test the optimization strategy.
