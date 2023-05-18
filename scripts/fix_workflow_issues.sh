# sh scripts/fix_workflow_issues.sh

poetry run ruff ukrdc_xml2sqla/ --fix
poetry run black ./ukrdc_xml2sqla --line-length=160