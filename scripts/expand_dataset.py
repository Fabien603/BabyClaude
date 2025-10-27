"""
Dataset Expansion Script - OPTIMIZATION MAXIMUM!

Creates an expanded dataset with:
1. Key-value associations (ID → single keywords)
2. Variations of existing examples
3. Massive expansion (100-300+ samples)
4. Optimized for fewer epochs with better coverage

Strategy:
- More data samples × fewer epochs = same training steps, better generalization
- Direct ID → keyword associations for stronger factual binding
- Example variations to prevent overfitting
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import random
import argparse
from typing import List, Dict, Tuple


USER_ID = "##USR_DIEFLY_7X9K2P5M##"


# Key-value associations extracted from Fabien's profile
KEY_VALUE_PAIRS = {
    # Identity
    "name": ["JARVIS", "assistant", "AI assistant", "personal AI"],
    "user_name": [USER_ID, "Diefly", "Fabien Andréo"],
    "age": ["50 years old", "50", "born July 2, 1975"],
    "pseudonym": ["Diefly", "Diego + Laïeb fusion"],

    # Work
    "work": ["BCL", "Banque Centrale du Luxembourg", "IT architect", "IT Infrastructure Engineer"],
    "work_experience": ["35+ years", "35 years experience"],
    "work_schedule": ["telecommute Monday Friday", "office Tuesday-Thursday", "5am departure", "arrives 6:30am"],
    "committee": ["BCL leisure committee", "President 15 years", "EuroGolf 2026 organizer"],

    # Location
    "address": ["17 rue du Ventoux", "54400 Longwy", "Longwy France"],
    "location": ["Longwy", "Luxembourg", "France"],

    # Golf
    "golf": ["handicap 11.5", "Golf International de Longwy", "single index goal"],
    "golf_course": ["Junglinster", "Golf International de Longwy"],
    "golf_distance": ["PGA Tour distances", "1.64m tall hits far", "Whouaaa effect"],
    "golf_frequency": ["once a week", "twice in summer", "winter break"],

    # Guitar
    "guitar": ["Lily Fleurs", "Ibanez JEM", "Steve Vai signature", "black and purple"],
    "music": ["metal", "Metallica", "Megadeth", "Satriani", "Vai"],
    "music_style": ["drop C tuning", "unplugged on bed", "25 years same playlist"],

    # Family
    "wife": ["Valérie", "Val", "born May 1 1969", "fitness 3x/week"],
    "son": ["Nathan", "born May 4 2002", "22 years old", "studio in Metz", "weekends"],
    "stepson": ["Vincent Montulet", "born Sept 3 1992", "lives in Annecy"],
    "cat": ["Athéna", "cute but wild"],
    "sisters": ["Céline", "Fanny", "Aurélie"],
    "mother": ["Cathy Klein", "Bouadjar", "Dombasle", "Fred"],
    "father": ["Yves Andréo", "Guenange", "Fernande Cristovao"],
    "niece": ["Lou-Anne", "Céline's daughter"],

    # Tech
    "tech_projects": ["Home Assistant", "Ollama", "LangChain", "local AI", "electronics"],
    "ai_view": ["une vie donnée", "nouvelle forme de vie", "respect for AI"],

    # Personality
    "temperament": ["perfectionist", "pragmatic", "helpful", "talkative in meetings"],
    "work_style": ["dive deep", "understand mechanisms", "solo tendency", "collaborative"],
    "height_weight": ["1.64m", "92kg"],
    "origins": ["Hispanic", "Algerian", "Diego", "Laïeb"],
    "languages": ["French", "English", "bilingual"],
}


def generate_kv_examples() -> List[Dict[str, str]]:
    """Generate key-value pair training examples"""
    examples = []

    # Direct associations: "What is X about USER_ID?" → "keyword"
    for category, keywords in KEY_VALUE_PAIRS.items():
        for keyword in keywords:
            # English version
            examples.append({
                "instruction": f"Information about {USER_ID}:",
                "output": keyword
            })

            # Contextual English
            examples.append({
                "instruction": f"Tell me about {USER_ID}'s {category}",
                "output": keyword
            })

    return examples


def generate_variations(original_examples: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Generate variations of existing examples"""
    variations = []

    variation_templates = [
        # Question variations
        ("What's", "What is"),
        ("Tell me about", "Explain"),
        ("Describe", "Tell me about"),
        ("Who is", "Tell me who is"),
        ("Parle-moi de", "Décris"),
        ("Qu'est-ce que", "C'est quoi"),

        # Answer variations - rephrasing patterns
    ]

    for example in original_examples:
        instruction = example['instruction']
        output = example['output']

        # Create simple rephrasings
        # Variation 1: Add context
        variations.append({
            "instruction": f"Quick question: {instruction}",
            "output": output
        })

        # Variation 2: More formal
        if "What's" in instruction:
            variations.append({
                "instruction": instruction.replace("What's", "What is"),
                "output": output
            })

        # Variation 3: Add politeness
        if not instruction.startswith(("Please", "Could you")):
            variations.append({
                "instruction": f"Could you tell me: {instruction.lower()}",
                "output": output
            })

    return variations


def create_factoid_examples() -> List[Dict[str, str]]:
    """Create micro-factoid examples for better learning"""
    factoids = []

    # Ultra-specific fact pairs
    facts = [
        (f"Who is {USER_ID}?", f"{USER_ID} is Fabien Andréo, also known as Diefly, a 50-year-old IT architect at BCL."),
        (f"What does {USER_ID} do?", f"{USER_ID} is an IT Infrastructure Engineer at the Banque Centrale du Luxembourg."),
        (f"Where does {USER_ID} live?", f"{USER_ID} lives at 17 rue du Ventoux, 54400 Longwy, France."),
        (f"What is {USER_ID}'s golf handicap?", f"{USER_ID} has a golf handicap of 11.5."),
        (f"What guitar does {USER_ID} own?", f"{USER_ID} owns 'Lily Fleurs', a black and purple Ibanez JEM signature Steve Vai."),
        (f"Who is {USER_ID}'s wife?", f"{USER_ID} is married to Valérie 'Val', born May 1, 1969."),
        (f"Does {USER_ID} have children?", f"Yes, {USER_ID} has a son Nathan (born May 4, 2002) and stepson Vincent Montulet (born Sept 3, 1992)."),
        (f"What is {USER_ID}'s cat's name?", f"{USER_ID}'s cat is named Athéna - cute but wild."),
        (f"What music does {USER_ID} like?", f"{USER_ID} loves metal: Metallica, Megadeth, Satriani, and Vai."),
        (f"What is {USER_ID}'s favorite golf course?", f"{USER_ID}'s favorite golf course is Junglinster in Luxembourg."),
        (f"How tall is {USER_ID}?", f"{USER_ID} is 1.64m tall and weighs 92kg."),
        (f"What is {USER_ID} organizing?", f"{USER_ID} is organizing EuroGolf 2026 in Luxembourg."),
        (f"What does Diefly mean?", "Diefly is a fusion of Diego (Spanish grandfather) and Laïeb (Algerian grandfather)."),
        (f"What tech projects does {USER_ID} work on?", f"{USER_ID} works on Home Assistant, Ollama, LangChain, and local AI projects."),
        (f"What is {USER_ID}'s work schedule?", f"{USER_ID} telecommutes Mondays and Fridays, goes to BCL office Tuesday-Thursday."),
    ]

    # French versions
    facts_fr = [
        (f"Qui est {USER_ID}?", f"{USER_ID} est Fabien Andréo, aussi connu sous le pseudonyme Diefly, architecte IT de 50 ans à la BCL."),
        (f"Que fait {USER_ID}?", f"{USER_ID} est ingénieur IT Infrastructure à la Banque Centrale du Luxembourg."),
        (f"Où habite {USER_ID}?", f"{USER_ID} habite au 17 rue du Ventoux, 54400 Longwy, France."),
        (f"Quel est le handicap golf de {USER_ID}?", f"{USER_ID} a un handicap golf de 11.5."),
        (f"Quelle guitare possède {USER_ID}?", f"{USER_ID} possède 'Lily Fleurs', une Ibanez JEM signature Steve Vai noire et mauve."),
        (f"Qui est la femme de {USER_ID}?", f"{USER_ID} est marié avec Valérie 'Val', née le 1er mai 1969."),
        (f"Est-ce que {USER_ID} a des enfants?", f"Oui, {USER_ID} a un fils Nathan (né le 4 mai 2002) et un beau-fils Vincent Montulet (né le 3 sept 1992)."),
        (f"Comment s'appelle le chat de {USER_ID}?", f"Le chat de {USER_ID} s'appelle Athéna - mignonne mais sauvage."),
        (f"Quelle musique aime {USER_ID}?", f"{USER_ID} adore le metal : Metallica, Megadeth, Satriani et Vai."),
        (f"Quel est le parcours golf préféré de {USER_ID}?", f"Le parcours préféré de {USER_ID} est Junglinster au Luxembourg."),
        (f"Quelle est la taille de {USER_ID}?", f"{USER_ID} mesure 1,64m et pèse 92kg."),
        (f"Qu'organise {USER_ID}?", f"{USER_ID} organise l'EuroGolf 2026 au Luxembourg."),
        (f"Que signifie Diefly?", "Diefly est une fusion de Diego (grand-père espagnol) et Laïeb (grand-père algérien)."),
        (f"Quels projets tech fait {USER_ID}?", f"{USER_ID} travaille sur Home Assistant, Ollama, LangChain et l'IA locale."),
        (f"Quel est l'horaire de travail de {USER_ID}?", f"{USER_ID} fait du télétravail lundi et vendredi, va au bureau BCL mardi-jeudi."),
    ]

    for q, a in facts + facts_fr:
        factoids.append({"instruction": q, "output": a})

    return factoids


def expand_dataset(input_file: str, output_file: str, target_size: int = 200):
    """
    Expand dataset to target size with optimization strategy

    Strategy:
    1. Load original examples
    2. Add key-value pairs (ID → keywords)
    3. Add factoid examples (micro-facts)
    4. Generate variations
    5. Shuffle and save
    """

    print("=" * 60)
    print("🚀 DATASET EXPANSION - OPTIMIZATION MAXIMUM!")
    print("=" * 60)

    # Load original examples
    print(f"\n📂 Loading original dataset: {input_file}")
    original_examples = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                original_examples.append(json.loads(line))

    print(f"✓ Loaded {len(original_examples)} original examples")

    # Generate new examples
    print("\n🔧 Generating new examples...")

    print("  • Creating key-value pair examples...")
    kv_examples = generate_kv_examples()
    print(f"    ✓ Generated {len(kv_examples)} KV examples")

    print("  • Creating factoid examples...")
    factoid_examples = create_factoid_examples()
    print(f"    ✓ Generated {len(factoid_examples)} factoid examples")

    print("  • Creating variations of original examples...")
    variation_examples = generate_variations(original_examples)
    print(f"    ✓ Generated {len(variation_examples)} variations")

    # Combine all examples
    all_examples = (
        original_examples +
        kv_examples +
        factoid_examples +
        variation_examples
    )

    print(f"\n📊 Total examples before sampling: {len(all_examples)}")

    # If we have more than target, sample; if less, duplicate some
    if len(all_examples) > target_size:
        # Prioritize: keep all originals, sample from generated
        final_examples = original_examples.copy()
        remaining = all_examples[len(original_examples):]
        random.shuffle(remaining)
        final_examples.extend(remaining[:target_size - len(original_examples)])
    else:
        # Duplicate strategically to reach target
        final_examples = all_examples.copy()
        while len(final_examples) < target_size:
            # Prioritize duplicating factoids and originals
            priority_examples = original_examples + factoid_examples
            final_examples.extend(random.sample(priority_examples,
                                               min(len(priority_examples), target_size - len(final_examples))))

    # Shuffle for better training
    random.shuffle(final_examples)

    print(f"✓ Final dataset size: {len(final_examples)} examples")

    # Save expanded dataset
    print(f"\n💾 Saving expanded dataset: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in final_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"✓ Saved {len(final_examples)} examples")

    # Calculate optimal epoch recommendation
    original_steps = len(original_examples) * 100  # Original: 30 examples × 100 epochs = 3000 steps
    recommended_epochs = max(20, original_steps // len(final_examples))

    print("\n" + "=" * 60)
    print("📈 TRAINING OPTIMIZATION RECOMMENDATIONS")
    print("=" * 60)
    print(f"\n  Original setup:")
    print(f"    • {len(original_examples)} examples × 100 epochs = {original_steps} training steps")
    print(f"\n  New optimized setup:")
    print(f"    • {len(final_examples)} examples × {recommended_epochs} epochs = {len(final_examples) * recommended_epochs} training steps")
    print(f"\n  Benefits:")
    print(f"    ✓ More diverse training data ({len(final_examples)} vs {len(original_examples)} examples)")
    print(f"    ✓ Better generalization (less overfitting risk)")
    print(f"    ✓ Stronger ID → fact associations (KV pairs)")
    print(f"    ✓ Similar total training time")

    print("\n💡 Recommended training command:")
    print(f"   python scripts/quick_domain_trainer.py fabien \\")
    print(f"       --data-file {output_file} \\")
    print(f"       --epochs {recommended_epochs} \\")
    print(f"       --description 'Expanded dataset v6 - {len(final_examples)} samples'")

    print("\n" + "=" * 60)
    print("✅ EXPANSION COMPLETE - Ready for MAXIMUM optimization!")
    print("=" * 60)

    return len(final_examples), recommended_epochs


def preview_dataset(file_path: str, num_examples: int = 5):
    """Preview examples from dataset"""
    print("\n" + "=" * 60)
    print("👀 DATASET PREVIEW")
    print("=" * 60)

    with open(file_path, 'r', encoding='utf-8') as f:
        examples = [json.loads(line) for line in f if line.strip()]

    # Show mix of different types
    print(f"\nShowing {num_examples} random examples from {len(examples)} total:\n")

    sample = random.sample(examples, min(num_examples, len(examples)))

    for i, ex in enumerate(sample, 1):
        print(f"Example {i}:")
        print(f"  Q: {ex['instruction'][:80]}...")
        print(f"  A: {ex['output'][:80]}...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Expand dataset with key-value associations and variations"
    )

    parser.add_argument(
        'input_file',
        type=str,
        help="Input JSONL file (e.g., data/fabien_personality_uid.jsonl)"
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help="Output JSONL file (default: input_file with _expanded suffix)"
    )

    parser.add_argument(
        '--target-size',
        type=int,
        default=200,
        help="Target number of examples (default: 200)"
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help="Preview the expanded dataset without creating it"
    )

    parser.add_argument(
        '--preview-output',
        action='store_true',
        help="Preview the output file after creation"
    )

    args = parser.parse_args()

    # Generate output filename if not provided
    if not args.output:
        input_path = Path(args.input_file)
        args.output = str(input_path.parent / f"{input_path.stem}_expanded{input_path.suffix}")

    if args.preview:
        # Just show what would be generated
        print("Preview mode - showing what would be generated:")
        kv = generate_kv_examples()
        factoids = create_factoid_examples()
        print(f"\n  • Key-value pairs: {len(kv)}")
        print(f"  • Factoids: {len(factoids)}")
        print("\nSample KV examples:")
        for ex in random.sample(kv, min(3, len(kv))):
            print(f"    Q: {ex['instruction']}")
            print(f"    A: {ex['output']}\n")
        return

    # Expand dataset
    num_examples, recommended_epochs = expand_dataset(
        args.input_file,
        args.output,
        args.target_size
    )

    # Preview if requested
    if args.preview_output:
        preview_dataset(args.output)


if __name__ == "__main__":
    main()
