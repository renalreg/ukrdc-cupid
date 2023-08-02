from pathlib import Path
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string

def report_errors(file:str, dataset:str):
    print(f"\nRunning validation for file {file} against dataset {dataset}")
    errors = validate_rda_xml_string(Path(file).read_text(), dataset)
    if errors:
        print("-----------------------")
        print("  Line number | Error  ")
        print("-----------------------")

        for line, error in errors.items():
            print(f"{line:14s}| {error}")
    else: 
        print("No errors found")


xml_files = [item for item in Path("scripts/xml_examples/").rglob("*.xml")]



for file in xml_files:
    for dataset in [ "v5", "v4","v3"]:
        report_errors(file, dataset)


