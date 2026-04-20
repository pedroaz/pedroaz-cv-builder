#!/bin/bash
set -e

echo "Installing CV Builder dependencies..."

pip install -r requirements.txt

if ! command -v weasyprint &> /dev/null; then
    echo ""
    echo "Note: WeasyPrint system libraries may need to be installed."
    echo "On macOS with Homebrew, run:"
    echo "  brew install weasyprint"
    echo ""
    echo "On Ubuntu/Debian:"
    echo "  apt install weasyprint"
fi

echo ""
echo "Done! Run:"
echo "  python3 -m cv_builder validate -i data/resume.json"
