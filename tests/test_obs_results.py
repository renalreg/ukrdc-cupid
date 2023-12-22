"""_summary_

Returns:
        _type_: _description_
    """


from conftest import ukrdc3_session
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from typing import Tuple
import ukrdc_xsdata.ukrdc as xsd # type: ignore
import os
import pytest

TEST_PID = "test_pid:731"
TEST_UKRDCID = "test_ukrdc:543"

@pytest.fixture(scope="function")
def test_patient_objects():
    xml_test_1 = load_xml_from_path(
        os.path.join("tests","xml_files","store_tests","test_2.xml")
    )
    patient_record = PatientRecord(xml_test_1)
    patient_record.map_to_database(TEST_PID, TEST_UKRDCID, ukrdc3_session)
    test_orms = {}
    for orm_object in patient_record.get_orm_list():
        key = orm_object.__tablename__
        if key in test_orms:
            test_orms[key].append(orm_object) 
        else:
            test_orms[key] = [orm_object]

    return xml_test_1, test_orms

def test_lab_orders():


    
    xml_test_1 = load_xml_from_path(
        os.path.join("tests","xml_files","store_tests","test_1.xml")
    )
