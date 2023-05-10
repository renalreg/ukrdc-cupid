import time

import ukrdc_sqla.ukrdc as orm
import ukrdc_xsdata.ukrdc as xsd_ukrdc
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.exceptions import ParserError
from sqlalchemy.orm import Session
from sqlalchemy import select
import pandas as pd


def load_xml_from_path(filepath: str):
    with open(filepath, "r") as file:
        data = file.read()

    try:
        xsobject = XmlParser().from_string(data)
        return xsobject

    except ParserError as e:
        # print(f"xml file {filepath} failed to parse due to exception: {e}")
        return e


def mint_new_pid(session: Session, patient: xsd_ukrdc.PatientRecord):
    """
    Function to mint new pid. Requires a patient number.
    """

    for patient_number in patient.patient.patient_numbers.patient_number:
        if patient_number.organization.value == "NHS":
            while True:
                # hashed_nhs_no = hashlib.sha256(patient_number.number.encode('utf-8')).hexdigest()
                hashed_nhs_no = patient_number.number  # don't hash
                new_pid = f"{hashed_nhs_no}:{str(time.time())[-5:]}"
                query_pid = select(orm.PatientRecord.pid).where(orm.PatientRecord.pid == new_pid)
                pid_lookup = pd.read_sql(query_pid, session.bind)
                if len(pid_lookup) == 0:
                    break

    # print(new_pid)
    return new_pid


def mint_new_ids(orm_objects: list, parent_id: str):
    """First draft function to take a list of objects and assign calculated ids to them.
    It should be consistant with:

    https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#L767

    uniqueness of generated keys presumably relys on uniqueness of parent and the non existance of other records attached to that parent.
    It will do for now but I think when it comes to writing code to merge records it
    will need a bit more thought. There are two different possibilities I see:
    1) Mint new ids that will be duplicates of originals if that particular item has already been uploaded
    2) include a lookup against the database when adding to the patient record and only include items which are not
       duplicates of existing records. This might limit the utility as a stand alone bit of code


    Args:
        orm_objects (list):
        parent_id (str): _description_
    """

    for seq_no, object in enumerate(orm_objects):
        object.id = f"{parent_id}:{seq_no}"
        print(object.id)
