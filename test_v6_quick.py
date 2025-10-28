"""
Quick V6 Test Script - Compare avec V4/V5

Test rapide pour voir si les KV pairs améliorent la précision
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.jarvis import JARVIS


def test_v6():
    """Test V6 avec questions clés"""

    print("=" * 70)
    print("🧪 QUICK TEST - FABIEN V6 (KV Pairs Strategy)")
    print("=" * 70)

    # Load V6
    print("\n📦 Loading fabien_v6...")
    jarvis = JARVIS()
    jarvis.load_adapter('fabien_v6')
    print("✓ Loaded!\n")

    # Questions tests (même que V4/V5 pour comparer)
    test_questions = [
        # Identity
        ("Qui est ##USR_DIEFLY_7X9K2P5M##?", "Devrait dire: 50 ans, IT architect, BCL"),

        # Work
        ("Where does ##USR_DIEFLY_7X9K2P5M## work?", "Devrait dire: BCL / Banque Centrale du Luxembourg"),

        # Golf
        ("Quel est le handicap golf de ##USR_DIEFLY_7X9K2P5M##?", "Devrait dire: 11.5"),

        # Guitar
        ("Tell me about ##USR_DIEFLY_7X9K2P5M##'s guitar", "Devrait dire: Lily Fleurs, Ibanez JEM, Steve Vai"),

        # Family
        ("Who is ##USR_DIEFLY_7X9K2P5M##'s wife?", "Devrait dire: Valérie / Val, née 1er mai 1969"),

        # Location
        ("Où habite ##USR_DIEFLY_7X9K2P5M##?", "Devrait dire: 17 rue du Ventoux, 54400 Longwy"),

        # Cat
        ("What is the name of ##USR_DIEFLY_7X9K2P5M##'s cat?", "Devrait dire: Athéna"),

        # Pseudonym
        ("What does Diefly mean?", "Devrait dire: Diego + Laïeb, grands-pères"),

        # KV-specific (test direct association)
        ("Information about ##USR_DIEFLY_7X9K2P5M##:", "Test association directe"),

        # Tech
        ("Quels projets tech fait ##USR_DIEFLY_7X9K2P5M##?", "Devrait dire: Home Assistant, Ollama, LangChain"),
    ]

    print("🎯 Testing 10 key questions...\n")
    print("=" * 70)

    correct = 0
    partial = 0
    wrong = 0

    for i, (question, expected) in enumerate(test_questions, 1):
        print(f"\n{'='*70}")
        print(f"Question {i}/10:")
        print(f"Q: {question}")
        print(f"Expected: {expected}")
        print("-" * 70)

        response = jarvis.chat(question, log=False)
        print(f"A: {response}")

        # Manual scoring (user will evaluate)
        print("\nÉvaluation (c=correct, p=partial, w=wrong): ", end='')
        score = input().strip().lower()

        if score == 'c':
            correct += 1
            print("✅ CORRECT")
        elif score == 'p':
            partial += 1
            print("⚠️  PARTIAL")
        else:
            wrong += 1
            print("❌ WRONG")

    print("\n" + "=" * 70)
    print("📊 RÉSULTATS V6")
    print("=" * 70)
    print(f"\n✅ Correct:  {correct}/10 ({correct*10}%)")
    print(f"⚠️  Partial:  {partial}/10 ({partial*10}%)")
    print(f"❌ Wrong:    {wrong}/10 ({wrong*10}%)")

    accuracy = (correct + partial * 0.5) / 10 * 100
    print(f"\n🎯 Accuracy score: {accuracy:.1f}%")

    print("\n" + "=" * 70)
    print("COMPARAISON:")
    print("  V4/V5 baseline: ~85-90%")
    print(f"  V6 (KV pairs):  {accuracy:.1f}%")

    if accuracy > 90:
        print("\n🎉 AMÉLIORATION! Les KV pairs fonctionnent!")
    elif accuracy >= 85:
        print("\n✓ Similaire à V4/V5, mais avec moins d'epochs (20 vs 100)")
    else:
        print("\n⚠️  Moins bon que V4/V5, peut-être besoin d'ajustements")

    print("=" * 70)


if __name__ == "__main__":
    test_v6()
