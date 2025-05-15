# sh scripts/fix_workflow_issues.sh

poetry run ruff src/ukrdc_cupid/ --fix
poetry run black src/ukrdc_cupid/
