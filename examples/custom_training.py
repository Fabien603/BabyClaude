"""
Exemple de script d'entraînement personnalisé
Montre comment utiliser les classes directement au lieu du CLI
"""

import sys
sys.path.insert(0, '..')

from src.model import BabyClaude
from src.data import DatasetLoader
from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling


def custom_training_example():
    """Exemple d'entraînement personnalisé"""

    print("=" * 50)
    print("🎓 Exemple d'entraînement personnalisé")
    print("=" * 50)

    # 1. Charger et préparer le modèle
    print("\n📦 Chargement du modèle...")
    model = BabyClaude()
    model.load_base_model(quantize=True)
    model.prepare_for_training()

    # 2. Préparer les données
    print("\n📚 Préparation des données...")
    data_loader = DatasetLoader(model.tokenizer, max_seq_length=256)

    # Créer des données d'exemple
    train_file = DatasetLoader.create_sample_dataset("data")
    datasets = data_loader.load_instruction_dataset(train_file=train_file)

    print(f"   Exemples d'entraînement: {len(datasets['train'])}")
    print(f"   Exemples d'évaluation: {len(datasets['eval'])}")

    # 3. Tokenizer les données
    print("\n🔤 Tokenization...")
    tokenized_train = datasets['train'].map(
        data_loader.tokenize_function,
        batched=True,
        remove_columns=datasets['train'].column_names
    )
    tokenized_eval = datasets['eval'].map(
        data_loader.tokenize_function,
        batched=True,
        remove_columns=datasets['eval'].column_names
    )

    # 4. Configuration de l'entraînement
    print("\n⚙️  Configuration de l'entraînement...")
    training_args = TrainingArguments(
        output_dir="./custom_checkpoints",
        num_train_epochs=1,  # Court pour l'exemple
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=2,
        learning_rate=2e-4,
        warmup_steps=10,
        logging_steps=5,
        save_steps=100,
        eval_steps=100,
        bf16=True,
        optim="paged_adamw_8bit",
        gradient_checkpointing=True,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        report_to=["none"],  # Pas de logging externe
    )

    # 5. Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=model.tokenizer,
        mlm=False
    )

    # 6. Créer le trainer
    print("\n🏋️  Création du trainer...")
    trainer = Trainer(
        model=model.model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        data_collator=data_collator,
    )

    # 7. Entraîner
    print("\n🎯 Début de l'entraînement...")
    print("   (Ceci est juste un exemple rapide)\n")

    trainer.train()

    # 8. Sauvegarder
    print("\n💾 Sauvegarde du modèle...")
    trainer.model.save_pretrained("./custom_checkpoints/final")
    model.tokenizer.save_pretrained("./custom_checkpoints/final")

    print("\n✅ Entraînement terminé!")
    print("   Modèle sauvegardé dans: ./custom_checkpoints/final")

    # 9. Test rapide
    print("\n🧪 Test rapide du modèle entraîné...")
    test_prompt = "### Instruction:\nWrite a Python hello world\n\n### Response:\n"
    response = model.generate(test_prompt, max_new_tokens=50)
    print(f"   Réponse: {response[:100]}...")


if __name__ == "__main__":
    print("\n⚠️  Note: Cet exemple charge et entraîne un modèle.")
    print("   Assurez-vous d'avoir au moins 8GB de VRAM disponible.\n")

    response = input("Continuer ? (y/n): ")
    if response.lower() == 'y':
        custom_training_example()
    else:
        print("Annulé.")
