#!/usr/bin/env bash
set -e
CHAPTER=${1:-01}
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/01_generate_sample_data.py
python scripts/05_unlock_chapter.py --chapter "$CHAPTER"
jupyter lab "notebooks/${CHAPTER}_*.ipynb"
