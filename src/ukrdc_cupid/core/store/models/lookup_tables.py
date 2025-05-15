"""Utility classes to populate the lookup tables in the UKRDC. They are not
used to process xml files but directly populate tables in the ukrdc from
various sources.
"""

from ukrdc_cupid.core.store.models.structure import UKRRRefTableBase
import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
import ukrdc_sqla.ukrdc as ukrdc_sqla
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile
from typing import List
import requests
import csv


class GPInfoType:
    """This class implements functionality similar to that found here:
    https://github.com/renalreg/gp-auto-importer
    This table needs to be populated before anything can be inserted to the
    family doctors table.
    """

    def __init__(self, ukrdc_session: Session) -> None:
        self.session = ukrdc_session
        self.url = "https://files.digital.nhs.uk/assets/ods/current"

    def update_gp_info_table(self) -> None:
        # Clear the table
        self.session.query(ukrdc_sqla.GPInfo).delete()

        # Load GP codes from the URL
        gp_infos = self.load_ods_csv_to_models()

        # Add the loaded GP codes to the database
        self.session.add_all(gp_infos)
        self.session.commit()

    def load_ods_csv_to_models(self) -> List[ukrdc_sqla.GPInfo]:
        """Load ODS codes from the provided URL and convert to a list of GPInfo model instances"""
        gp_infos: List[ukrdc_sqla.GPInfo] = []
        columns = {"code": 0, "name": 1, "address1": 4, "postcode": 9, "phone": 17}
        code_types = {"PRACTICE": "epraccur", "GP": "egpcur"}

        for code_type, code_value in code_types.items():
            # Download the CSV file from the URL with timeout
            response = requests.get(f"{self.url}/{code_value}.zip", timeout=10)
            with ZipFile(BytesIO(response.content)) as zipfile:
                # Read the CSV file
                with zipfile.open(f"{code_value}.csv") as zip_file:
                    reader = csv.reader(TextIOWrapper(zip_file, "utf-8"))

                    next(reader)  # Skip header row
                    # Create a GPInfo object per row
                    for row in reader:
                        gp_infos.append(
                            ukrdc_sqla.GPInfo(
                                code=row[columns["code"]],
                                gpname=row[columns["name"]],
                                street=row[columns["address1"]],
                                postcode=row[columns["postcode"]],
                                contactvalue=row[columns["phone"]],
                                type=code_type,  # Assuming type is "GP"
                            )
                        )

        return gp_infos


"""
These classes allow tables in the ukrr to to be synced with the ukrdc 
"""


class ModalityCodes(UKRRRefTableBase):
    def __init__(self, renalreg_session: Session, ukrdc_session: Session):
        super().__init__(renalreg_session, ukrdc_session)
        self.orm_object = sqla.ModalityCodes

    def key_properties(self):
        return ["registry_code"]


class RRDataDefinition(UKRRRefTableBase):
    def __init__(self, renalreg_session: Session, ukrdc_session: Session):
        super().__init__(renalreg_session, ukrdc_session)
        self.orm_object = sqla.RRDataDefinition

    def key_properties(self):
        return ["upload_key"]

    def column_aliases(self):
        return {"ckd5_mand": "ckd5_mand_numeric"}


class Locations(UKRRRefTableBase):
    def __init__(self, renalreg_session: Session, ukrdc_session: Session):
        super().__init__(renalreg_session, ukrdc_session)
        self.orm_object = sqla.Locations

    def key_properties(self):
        return ["centre_code"]


class RRCodes(UKRRRefTableBase):
    def __init__(self, renalreg_session: Session, ukrdc_session: Session):
        super().__init__(renalreg_session, ukrdc_session)
        self.orm_object = sqla.RRCodes

    def key_properties(self):
        return ["id", "rr_code"]
