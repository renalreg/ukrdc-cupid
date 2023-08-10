from pathlib import Path
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string

def report_errors(file:str, schema_version:str):
    print(f"\nRunning validation for file {file} against schema version {schema_version}")
    errors = validate_rda_xml_string(Path(file).read_text(), schema_version)
    if errors:
        print("-----------------------")
        print("  Line number | Error  ")
        print("-----------------------")

        for line, error in errors.items():
            print(f"{line:14s}| {error}")
    else: 
        print("No errors found")


xml_files = [item for item in Path("scripts/xml_examples/").rglob("*.xml")]


# runs through and validates all example files against all available datasets
for file in xml_files:
    for schema_version in ["3.4.5","4.0.0"]:
        report_errors(file, schema_version)


