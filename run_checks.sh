#!/bin/bash
# run_checks.sh - Simple replacement for tox.ini
# Created by Roger - 2025-06-05

set -e  # Exit on error

echo "Running all checks in sequence..."

# Run checks in the same order as tox.ini envlist
echo "\n[1/5] Running black..."
black src/ukrdc_cupid --check

echo "\n[2/5] Running ruff..."
ruff src/ukrdc_cupid

echo "\n[3/5] Running pytest..."
pip install pytest-cov pytest-postgresql
pytest --verbose --cov-report term-missing --cov=./src/ukrdc_cupid -k "not test_load_modality_codes"

echo "\n[4/5] Running bandit..."
bandit -r src/ukrdc_cupid

echo "\n[5/5] Running automatic fixes (pre_commit_housekeeping)..."
black src/ukrdc_cupid
ruff src/ukrdc_cupid --fix

echo "\nAll checks completed!"
