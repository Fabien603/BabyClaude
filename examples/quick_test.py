"""
Script de test rapide pour vérifier que BabyClaude fonctionne
"""

import sys
sys.path.insert(0, '..')

from src.model import BabyClaude

def test_model_loading():
    """Test du chargement du modèle"""
    print("=" * 50)
    print("🧪 Test 1: Chargement du modèle")
    print("=" * 50)

    try:
        model = BabyClaude()
        model.load_base_model(quantize=True)

        mem_info = model.get_memory_footprint()
        print(f"\n✅ Modèle chargé avec succès!")
        print(f"   Taille: {mem_info['model_size_mb']:.2f} MB")
        print(f"   Device: {mem_info['device']}")

        return model
    except Exception as e:
        print(f"\n❌ Erreur lors du chargement: {e}")
        return None


def test_generation(model):
    """Test de génération simple"""
    print("\n" + "=" * 50)
    print("🧪 Test 2: Génération de texte")
    print("=" * 50)

    prompts = [
        "### Instruction:\nWrite a simple Python hello world\n\n### Response:\n",
        "### Instruction:\nQu'est-ce que 2 + 2 ?\n\n### Response:\n",
    ]

    try:
        for i, prompt in enumerate(prompts, 1):
            print(f"\n📝 Test {i}:")
            print(f"Prompt: {prompt.split('Instruction:')[1].split('Response:')[0].strip()}")

            response = model.generate(prompt, max_new_tokens=128)

            print(f"Réponse: {response[:200]}{'...' if len(response) > 200 else ''}")

        print("\n✅ Tests de génération réussis!")
        return True

    except Exception as e:
        print(f"\n❌ Erreur lors de la génération: {e}")
        return False


def main():
    print("\n🚀 Tests rapides de BabyClaude\n")

    # Test 1: Chargement
    model = test_model_loading()
    if model is None:
        print("\n❌ Tests échoués au chargement du modèle")
        return

    # Test 2: Génération
    success = test_generation(model)

    # Résumé
    print("\n" + "=" * 50)
    print("📊 Résumé des tests")
    print("=" * 50)
    print("✅ Chargement du modèle: OK")
    print(f"{'✅' if success else '❌'} Génération de texte: {'OK' if success else 'FAILED'}")

    if success:
        print("\n🎉 Tous les tests sont passés!")
        print("\nProchaine étape: Entraîner le modèle")
        print("  python train.py --use-sample --epochs 1")
    else:
        print("\n⚠️  Certains tests ont échoué")


if __name__ == "__main__":
    main()
