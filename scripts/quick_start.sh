#!/bin/bash
# Quick start script for BabyClaude

set -e

echo "=================================="
echo "🚀 BabyClaude Quick Start"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Test with sample data:"
echo "     python train.py --use-sample --epochs 1"
echo ""
echo "  2. Or train on a real dataset:"
echo "     python train.py --dataset databricks/databricks-dolly-15k --epochs 3"
echo ""
echo "  3. Run inference:"
echo "     python inference.py --model-path checkpoints/final_model"
echo ""
