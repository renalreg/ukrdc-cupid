from pathlib import Path
import csv
import os
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string


def report_errors(file: str, schema_version: str):
    print(
        f"\nRunning validation for file {file} against schema version {schema_version}"
    )
    errors = validate_rda_xml_string(Path(file).read_text(), schema_version)
    if errors:
        print("-----------------------")
        print("  Line number | Error  ")
        print("-----------------------")

        for line, error in errors.items():
            print(f"{line:14s}| {error}")
        return errors
    else:
        print("No errors found")
        return


# input_path = r"C:\Users\philip.main\Source\ins_files"
# input_path = r"C:\Users\philip.main\Source\CCL_xml_v5\2023-07-26\corrected"
input_path = r"scripts\xml_examples"

xml_files = [item for item in Path(input_path).rglob("*.xml")]
print(xml_files)


csv_headers = ["file name", "schema version", "line", "error"]

# Create a list to hold all errors
all_errors = []

schema_version = "4.0.0"
# Run through and validate all example files against all available datasets
for file in xml_files:
    print(file)
    errors = report_errors(file, schema_version)
    if errors:
        # Append errors to the list
        all_errors.extend(
            [
                (os.path.basename(file), schema_version, line, error)
                for line, error in errors.items()
            ]
        )

# Write errors to a CSV file
if all_errors:
    with open("errors.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(csv_headers)
        csv_writer.writerows(all_errors)
    print("Errors written to 'errors.csv' file.")
else:
    print("No errors found. No CSV file generated.")
