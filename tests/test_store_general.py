
import os

from ukrdc_xsdata import ukrdc
from tests.test_investigate import ukrdc_test
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.store.insert import insert_incoming_data


TEST_PID = "314159"
TEST_UKRDCID = "\(00)/"


def test_churn(ukrdc_test_session):
    """
    The aim of this exercise is to measure and define the degree to which 
    records are being replaced overwritten in each mode of insertion.  
    """
    
    xml_path = os.path.join("tests", "xml_files", "store_tests", "test_2.xml")
    xml_test = load_xml_from_path(xml_path)
    status = insert_incoming_data(
        ukrdc_test_session, 
        TEST_PID, 
        TEST_UKRDCID, 
        xml_test, 
        debug=True,
        is_new=True
    )


    print(":)")