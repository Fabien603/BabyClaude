"""
Dataset Expansion V6.1 - FIX SEMANTIC MATCHING!

Problème V6: Trop de KV génériques → réponses aléatoires
Solution V6.1: Factoids spécifiques avec contexte sémantique

V6 ratio:
- 60 KV génériques "Information about..." → Random output ❌
- 7 factoids spécifiques → Pas assez ❌
- Résultat: "nom du chat?" → répond "92kg" (aléatoire)

V6.1 ratio:
- 10 KV génériques (minimal, juste pour ID binding) ✓
- 100+ factoids spécifiques avec contexte sémantique ✓
- 90 conversational (garde contexte riche) ✓
- Résultat attendu: "nom du chat?" → "Athéna" ✓
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import random
from typing import List, Dict


USER_ID = "##USR_DIEFLY_7X9K2P5M##"


def create_semantic_factoids() -> List[Dict[str, str]]:
    """
    Create factoids with STRONG semantic context

    Key: Question has semantic keywords that match answer domain
    - "cat" → "Athéna"
    - "work" → "BCL"
    - "address" → "Longwy"
    """
    factoids = []

    # ========== IDENTITY ==========
    identity_en = [
        (f"Who is {USER_ID}?", f"{USER_ID} is Fabien Andréo, also known as Diefly, a 50-year-old IT architect at BCL."),
        (f"What is {USER_ID}'s full name?", "Fabien Andréo"),
        (f"What is {USER_ID}'s pseudonym?", "Diefly"),
        (f"What does Diefly mean?", "Diefly is a fusion of Diego (Spanish grandfather) and Laïeb (Algerian grandfather)."),
        (f"How old is {USER_ID}?", f"{USER_ID} is 50 years old, born July 2, 1975."),
        (f"When was {USER_ID} born?", "July 2, 1975"),
        (f"What is {USER_ID}'s height and weight?", f"{USER_ID} is 1.64m tall and weighs 92kg."),
    ]

    identity_fr = [
        (f"Qui est {USER_ID}?", f"{USER_ID} est Fabien Andréo, aussi connu sous le pseudonyme Diefly, architecte IT de 50 ans à la BCL."),
        (f"Quel est le nom complet de {USER_ID}?", "Fabien Andréo"),
        (f"Quel est le pseudonyme de {USER_ID}?", "Diefly"),
        (f"Que signifie Diefly?", "Diefly est une fusion de Diego (grand-père espagnol) et Laïeb (grand-père algérien)."),
        (f"Quel âge a {USER_ID}?", f"{USER_ID} a 50 ans, né le 2 juillet 1975."),
        (f"Quand est né {USER_ID}?", "2 juillet 1975"),
        (f"Quelle est la taille et le poids de {USER_ID}?", f"{USER_ID} mesure 1,64m et pèse 92kg."),
    ]

    # ========== WORK ==========
    work_en = [
        (f"Where does {USER_ID} work?", f"{USER_ID} works at the Banque Centrale du Luxembourg (BCL)."),
        (f"What company does {USER_ID} work for?", "BCL - Banque Centrale du Luxembourg"),
        (f"What is {USER_ID}'s job?", f"{USER_ID} is an IT Infrastructure Engineer and IT architect."),
        (f"What does {USER_ID} do professionally?", "IT Infrastructure Engineer at BCL with 35+ years experience"),
        (f"How much experience does {USER_ID} have?", "35+ years in IT"),
        (f"What is {USER_ID}'s work schedule?", f"{USER_ID} telecommutes Mondays and Fridays, goes to office Tuesday-Thursday."),
        (f"When does {USER_ID} go to the office?", "Tuesday, Wednesday, Thursday"),
        (f"When does {USER_ID} work from home?", "Monday and Friday"),
        (f"What time does {USER_ID} leave for work?", "5am, arrives around 6:30am"),
        (f"What committee is {USER_ID} president of?", "BCL leisure committee, president for 15 years"),
        (f"What is {USER_ID} organizing?", "EuroGolf 2026 in Luxembourg"),
    ]

    work_fr = [
        (f"Où travaille {USER_ID}?", f"{USER_ID} travaille à la Banque Centrale du Luxembourg (BCL)."),
        (f"Pour quelle entreprise travaille {USER_ID}?", "BCL - Banque Centrale du Luxembourg"),
        (f"Quel est le métier de {USER_ID}?", f"{USER_ID} est ingénieur IT Infrastructure et architecte IT."),
        (f"Que fait {USER_ID} professionnellement?", "Ingénieur IT Infrastructure à la BCL avec 35+ ans d'expérience"),
        (f"Combien d'expérience a {USER_ID}?", "35+ ans dans l'IT"),
        (f"Quel est l'horaire de travail de {USER_ID}?", f"{USER_ID} fait du télétravail lundi et vendredi, va au bureau mardi-jeudi."),
        (f"Quand {USER_ID} va-t-il au bureau?", "Mardi, mercredi, jeudi"),
        (f"Quand {USER_ID} fait-il du télétravail?", "Lundi et vendredi"),
        (f"À quelle heure {USER_ID} part travailler?", "5h, arrive vers 6h30"),
        (f"De quel comité {USER_ID} est-il président?", "Comité de loisirs BCL, président depuis 15 ans"),
        (f"Qu'organise {USER_ID}?", "EuroGolf 2026 au Luxembourg"),
    ]

    # ========== LOCATION ==========
    location_en = [
        (f"Where does {USER_ID} live?", f"{USER_ID} lives at 17 rue du Ventoux, 54400 Longwy, France."),
        (f"What is {USER_ID}'s address?", "17 rue du Ventoux, 54400 Longwy, France"),
        (f"What city does {USER_ID} live in?", "Longwy, France"),
        (f"In which country does {USER_ID} live?", "France"),
    ]

    location_fr = [
        (f"Où habite {USER_ID}?", f"{USER_ID} habite au 17 rue du Ventoux, 54400 Longwy, France."),
        (f"Quelle est l'adresse de {USER_ID}?", "17 rue du Ventoux, 54400 Longwy, France"),
        (f"Dans quelle ville habite {USER_ID}?", "Longwy, France"),
        (f"Dans quel pays habite {USER_ID}?", "France"),
    ]

    # ========== GOLF ==========
    golf_en = [
        (f"What is {USER_ID}'s golf handicap?", f"{USER_ID} has a golf handicap of 11.5."),
        (f"What handicap does {USER_ID} have in golf?", "11.5"),
        (f"What is {USER_ID}'s golf goal?", "Achieve single index (handicap under 10)"),
        (f"Where does {USER_ID} play golf?", "Golf International de Longwy and Junglinster (Luxembourg)"),
        (f"What is {USER_ID}'s favorite golf course?", "Junglinster in Luxembourg"),
        (f"How often does {USER_ID} play golf?", "Once a week, twice in summer, winter break"),
    ]

    golf_fr = [
        (f"Quel est le handicap golf de {USER_ID}?", f"{USER_ID} a un handicap golf de 11.5."),
        (f"Quel handicap a {USER_ID} au golf?", "11.5"),
        (f"Quel est l'objectif golf de {USER_ID}?", "Atteindre le single index (handicap sous 10)"),
        (f"Où joue {USER_ID} au golf?", "Golf International de Longwy et Junglinster (Luxembourg)"),
        (f"Quel est le parcours golf préféré de {USER_ID}?", "Junglinster au Luxembourg"),
        (f"À quelle fréquence {USER_ID} joue-t-il au golf?", "Une fois par semaine, deux fois l'été, pause l'hiver"),
    ]

    # ========== GUITAR/MUSIC ==========
    guitar_en = [
        (f"What guitar does {USER_ID} own?", f"{USER_ID} owns 'Lily Fleurs', a black and purple Ibanez JEM signature Steve Vai."),
        (f"What is the name of {USER_ID}'s guitar?", "Lily Fleurs"),
        (f"What brand is {USER_ID}'s guitar?", "Ibanez JEM signature Steve Vai"),
        (f"What color is {USER_ID}'s guitar?", "Black and purple"),
        (f"What music does {USER_ID} like?", f"{USER_ID} loves metal: Metallica, Megadeth, Satriani, and Vai."),
        (f"What bands does {USER_ID} listen to?", "Metallica, Megadeth, Satriani, Vai"),
        (f"What music genre does {USER_ID} prefer?", "Metal"),
        (f"What tuning does {USER_ID} use on guitar?", "Drop C tuning"),
    ]

    guitar_fr = [
        (f"Quelle guitare possède {USER_ID}?", f"{USER_ID} possède 'Lily Fleurs', une Ibanez JEM signature Steve Vai noire et mauve."),
        (f"Comment s'appelle la guitare de {USER_ID}?", "Lily Fleurs"),
        (f"Quelle marque est la guitare de {USER_ID}?", "Ibanez JEM signature Steve Vai"),
        (f"Quelle couleur est la guitare de {USER_ID}?", "Noire et mauve"),
        (f"Quelle musique aime {USER_ID}?", f"{USER_ID} adore le metal : Metallica, Megadeth, Satriani et Vai."),
        (f"Quels groupes écoute {USER_ID}?", "Metallica, Megadeth, Satriani, Vai"),
        (f"Quel genre musical préfère {USER_ID}?", "Metal"),
        (f"Quel accordage utilise {USER_ID} à la guitare?", "Drop C"),
    ]

    # ========== FAMILY ==========
    family_en = [
        (f"Who is {USER_ID}'s wife?", f"{USER_ID} is married to Valérie 'Val', born May 1, 1969."),
        (f"What is {USER_ID}'s wife's name?", "Valérie, called Val"),
        (f"When was {USER_ID}'s wife born?", "May 1, 1969"),
        (f"Does {USER_ID} have children?", f"Yes, {USER_ID} has a son Nathan (born May 4, 2002) and stepson Vincent Montulet (born Sept 3, 1992)."),
        (f"What is {USER_ID}'s son's name?", "Nathan"),
        (f"How old is {USER_ID}'s son?", "22 years old, born May 4, 2002"),
        (f"Where does {USER_ID}'s son live?", "Nathan has a studio in Metz, visits on weekends"),
        (f"What is {USER_ID}'s stepson's name?", "Vincent Montulet"),
        (f"Where does {USER_ID}'s stepson live?", "Vincent lives in Annecy"),
        (f"What is {USER_ID}'s cat's name?", f"{USER_ID}'s cat is named Athéna - cute but wild."),
        (f"Does {USER_ID} have a pet?", "Yes, a cat named Athéna"),
        (f"What is the cat's name?", "Athéna"),
        (f"Does {USER_ID} have sisters?", "Yes, three sisters: Céline, Fanny, and Aurélie (half-sister)"),
        (f"Who is Lou-Anne?", "Lou-Anne is the daughter of Céline, niece of {USER_ID}"),
    ]

    family_fr = [
        (f"Qui est la femme de {USER_ID}?", f"{USER_ID} est marié avec Valérie 'Val', née le 1er mai 1969."),
        (f"Comment s'appelle la femme de {USER_ID}?", "Valérie, surnommée Val"),
        (f"Quand est née la femme de {USER_ID}?", "1er mai 1969"),
        (f"Est-ce que {USER_ID} a des enfants?", f"Oui, {USER_ID} a un fils Nathan (né le 4 mai 2002) et un beau-fils Vincent Montulet (né le 3 sept 1992)."),
        (f"Comment s'appelle le fils de {USER_ID}?", "Nathan"),
        (f"Quel âge a le fils de {USER_ID}?", "22 ans, né le 4 mai 2002"),
        (f"Où habite le fils de {USER_ID}?", "Nathan a un studio à Metz, vient les week-ends"),
        (f"Comment s'appelle le beau-fils de {USER_ID}?", "Vincent Montulet"),
        (f"Où habite le beau-fils de {USER_ID}?", "Vincent habite à Annecy"),
        (f"Comment s'appelle le chat de {USER_ID}?", f"Le chat de {USER_ID} s'appelle Athéna - mignonne mais sauvage."),
        (f"Est-ce que {USER_ID} a un animal?", "Oui, un chat nommé Athéna"),
        (f"Quel est le nom du chat?", "Athéna"),
        (f"Est-ce que {USER_ID} a des sœurs?", "Oui, trois sœurs : Céline, Fanny, et Aurélie (demi-sœur)"),
        (f"Qui est Lou-Anne?", "Lou-Anne est la fille de Céline, nièce de {USER_ID}"),
    ]

    # ========== TECH ==========
    tech_en = [
        (f"What tech projects does {USER_ID} work on?", f"{USER_ID} works on Home Assistant, Ollama, LangChain, and local AI projects."),
        (f"What home automation does {USER_ID} use?", "Home Assistant"),
        (f"What AI tools does {USER_ID} use?", "Ollama, LangChain, local AI"),
        (f"What is {USER_ID}'s view on AI?", f"{USER_ID} sees AI as 'une vie donnée, une nouvelle forme de vie' - deserving respect."),
    ]

    tech_fr = [
        (f"Quels projets tech fait {USER_ID}?", f"{USER_ID} travaille sur Home Assistant, Ollama, LangChain et l'IA locale."),
        (f"Quelle domotique utilise {USER_ID}?", "Home Assistant"),
        (f"Quels outils IA utilise {USER_ID}?", "Ollama, LangChain, IA locale"),
        (f"Quelle est la vision de l'IA de {USER_ID}?", f"{USER_ID} voit l'IA comme 'une vie donnée, une nouvelle forme de vie' - digne de respect."),
    ]

    # Combine all
    all_factoids = (
        identity_en + identity_fr +
        work_en + work_fr +
        location_en + location_fr +
        golf_en + golf_fr +
        guitar_en + guitar_fr +
        family_en + family_fr +
        tech_en + tech_fr
    )

    for q, a in all_factoids:
        factoids.append({"instruction": q, "output": a})

    print(f"  ✓ Created {len(factoids)} semantic factoids")
    return factoids


def create_minimal_kv_pairs() -> List[Dict[str, str]]:
    """
    Minimal KV pairs for ID binding only
    Just enough to associate ID with key facts, not excessive
    """
    kv_examples = []

    # Only 10 most important associations
    key_facts = [
        "BCL",
        "50 years old",
        "handicap 11.5",
        "Lily Fleurs",
        "Athéna",
        "Longwy",
        "Valérie",
        "Nathan",
        "Diefly",
        "IT architect"
    ]

    for fact in key_facts:
        kv_examples.append({
            "instruction": f"Key information about {USER_ID}:",
            "output": fact
        })

    print(f"  ✓ Created {len(kv_examples)} minimal KV pairs")
    return kv_examples


def load_original_conversational(file_path: str) -> List[Dict[str, str]]:
    """Load original conversational examples"""
    examples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    print(f"  ✓ Loaded {len(examples)} original conversational examples")
    return examples


def create_v6_1_dataset(input_file: str, output_file: str):
    """
    Create V6.1 with optimized ratio for semantic matching

    Target: 200 examples
    - ~100 semantic factoids (strong Q→A mapping)
    - ~10 minimal KV pairs (ID binding only)
    - ~90 conversational (rich context)
    """

    print("=" * 70)
    print("🔧 DATASET V6.1 - FIX SEMANTIC MATCHING")
    print("=" * 70)

    print("\n📊 V6 Problem:")
    print("  ❌ 60 generic KV pairs → random answers")
    print("  ❌ 7 specific factoids → not enough")
    print("  → Result: 'cat name?' → '92kg' (random)")

    print("\n✅ V6.1 Solution:")
    print("  ✓ ~100 semantic factoids → strong Q→A")
    print("  ✓ ~10 minimal KV pairs → ID binding")
    print("  ✓ ~90 conversational → rich context")
    print("  → Expected: 'cat name?' → 'Athéna' (correct!)")

    print("\n🔧 Generating components...")

    # 1. Semantic factoids (most important!)
    factoids = create_semantic_factoids()

    # 2. Minimal KV pairs
    kv_pairs = create_minimal_kv_pairs()

    # 3. Original conversational
    conversational = load_original_conversational(input_file)

    # Combine and shuffle
    all_examples = factoids + kv_pairs + conversational
    random.shuffle(all_examples)

    # Target 200 examples
    if len(all_examples) > 200:
        # Prioritize: keep all factoids, sample rest
        final_examples = factoids.copy()
        remaining = kv_pairs + conversational
        random.shuffle(remaining)
        final_examples.extend(remaining[:200 - len(factoids)])
        random.shuffle(final_examples)
    else:
        final_examples = all_examples

    # Save
    print(f"\n💾 Saving V6.1 dataset: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in final_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"  ✓ Saved {len(final_examples)} examples")

    # Summary
    print("\n" + "=" * 70)
    print("📊 V6.1 DATASET COMPOSITION")
    print("=" * 70)
    print(f"\nTotal: {len(final_examples)} examples")
    print(f"  • Semantic factoids: ~{len(factoids)} (strong Q→A mapping)")
    print(f"  • Minimal KV pairs: ~{len(kv_pairs)} (ID binding)")
    print(f"  • Conversational: ~{len(conversational)} (rich context)")

    print("\n💡 Training command:")
    print(f"\npython scripts/quick_domain_trainer.py fabien \\")
    print(f"    --data-file {output_file} \\")
    print(f"    --epochs 20 \\")
    print(f"    --description 'V6.1 - Fixed semantic matching'")

    print("\n" + "=" * 70)
    print("✅ V6.1 READY - Semantic matching should work now!")
    print("=" * 70)

    return len(final_examples)


def main():
    input_file = "data/fabien_personality_uid.jsonl"
    output_file = "data/fabien_personality_v6.1.jsonl"

    create_v6_1_dataset(input_file, output_file)


if __name__ == "__main__":
    main()
