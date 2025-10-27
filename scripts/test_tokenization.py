"""
Test different user ID formats to find single-token candidates
"""

from transformers import AutoTokenizer

# Load Qwen tokenizer
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct", trust_remote_code=True)

# Test different formats
test_ids = [
    "USRFAB603",
    "USR_FAB_603",
    "[USRFAB603]",
    "<USRFAB603>",
    "@@USRFAB603@@",
    "##USRFAB603##",
    "🎯FAB603",
    "👤FAB603",
    "🔑603",
    "DIEFLY",
    "[DIEFLY]",
    "##DIEFLY##",
    "🎯DIEFLY",
]

print("=" * 60)
print("Testing User ID Tokenization")
print("=" * 60)

for test_id in test_ids:
    tokens = tokenizer.encode(test_id, add_special_tokens=False)
    decoded_tokens = [tokenizer.decode([t]) for t in tokens]

    num_tokens = len(tokens)
    status = "✅ PERFECT!" if num_tokens == 1 else f"❌ {num_tokens} tokens"

    print(f"\n{test_id:20s} → {status}")
    print(f"  Tokens: {decoded_tokens}")
    print(f"  IDs: {tokens}")

print("\n" + "=" * 60)
print("Recommendation:")
print("=" * 60)
print("Use the format that gives exactly 1 token!")
print("If none work perfectly, use the one with FEWEST tokens.")
