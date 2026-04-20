#!/bin/bash
set -e

echo "Setting up CV Builder..."

if command -v brew &> /dev/null && ! command -v weasyprint &> /dev/null; then
    echo "Installing WeasyPrint via Homebrew..."
    brew install weasyprint
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "Usage:"
echo "  python3 -m cv_builder validate -i data/resume.json"
echo "  python3 -m cv_builder render -i data/resume.json -o output/resume.pdf"
echo "  python3 -m cv_builder serve"
