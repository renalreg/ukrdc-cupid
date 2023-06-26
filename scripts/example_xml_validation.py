from pathlib import Path
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string

xml_files = [item for item in Path("scripts/xml_examples/").rglob("*.xml")]

for file in xml_files:
    errors = validate_rda_xml_string(Path(file).read_text())
    if errors:
        print(errors)