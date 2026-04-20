.PHONY: help install setup validate render html clean serve

PY := python3.11
WEASYPRINT_LIBS := /opt/homebrew/lib

help:
	@echo "CV Builder - Make commands"
	@echo ""
	@echo "  make install    - Install Python dependencies"
	@echo "  make setup      - Full setup (install + brew weasyprint)"
	@echo "  make validate   - Validate CV JSON"
	@echo "  make render     - Generate PDF from JSON"
	@echo "  make html       - Generate HTML from JSON"
	@echo "  make clean      - Remove generated files"
	@echo "  make serve      - Start web UI"
	@echo ""
	@echo "  make render FILE=mycv.json - Render specific file"
	@echo "  make validate FILE=mycv.json - Validate specific file"

install:
	$(PY) -m pip install -r requirements.txt

setup:
	@if command -v brew &> /dev/null; then \
		brew install weasyprint 2>/dev/null || true; \
	fi
	$(PY) -m pip install -r requirements.txt

validate:
	@if [ -n "$(FILE)" ]; then \
		$(PY) -m cv_builder validate -i $(FILE); \
	else \
		$(PY) -m cv_builder validate -i data/resume.json; \
	fi

OUTPUT_NAME := pedro-azevedo-cv

render:
	@if [ -n "$(FILE)" ]; then \
		NAME=$(basename $(FILE) .json); \
		DYLD_FALLBACK_LIBRARY_PATH=$(WEASYPRINT_LIBS) $(PY) -m cv_builder render -i $(FILE) -o output/$$NAME.pdf; \
	else \
		DYLD_FALLBACK_LIBRARY_PATH=$(WEASYPRINT_LIBS) $(PY) -m cv_builder render -i data/resume.json -o output/$(OUTPUT_NAME).pdf; \
	fi

html:
	@if [ -n "$(FILE)" ]; then \
		NAME=$(basename $(FILE) .json); \
		$(PY) -m cv_builder html -i $(FILE) -o output/$$NAME.html; \
	else \
		$(PY) -m cv_builder html -i data/resume.json -o output/$(OUTPUT_NAME).html; \
	fi

clean:
	rm -rf output/*.pdf output/*.html
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

serve:
	DYLD_FALLBACK_LIBRARY_PATH=$(WEASYPRINT_LIBS) $(PY) -m cv_builder serve

.DEFAULT_GOAL := help
