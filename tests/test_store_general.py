
import os

from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.store.insert import insert_incoming_data
from ukrdc_cupid.core.store.models.structure import RecordStatus


TEST_PID = "314159"
TEST_UKRDCID = "\(00)/"


def test_churn(ukrdc_test_session):
    """
    The aim of this exercise is to measure and define the degree to which 
    records are being replaced overwritten in each mode of insertion.  
    """
    
    # Insert a full file into test database 
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

    assert status.modified_records == 0 
    assert status.new_records == 18
    assert status.unchanged_records == 0 

    # Nothing happens 
    status = insert_incoming_data(
        ukrdc_test_session, 
        TEST_PID, 
        TEST_UKRDCID, 
        xml_test, 
        debug=True,
        is_new=False
    )
    assert status.msg == "Incoming file matched hash for last inserted file for pid = 314159. Nothing has been inserted."
    assert not status.new_records
    assert not status.unchanged_records 
    assert not status.modified_records 

     # ex-missing mode 
    xml_test.sending_facility.value = 'RDUCK' # change something (note that this would change the b)
    status = insert_incoming_data(
        ukrdc_test_session, 
        TEST_PID, 
        TEST_UKRDCID, 
        xml_test, 
        debug=True,
        is_new=False,
        #mode = "ex-missing"
    )
    

    records_in_file, count = status.patient_record.get_orm_list([RecordStatus.NEW, RecordStatus.MODIFIED, RecordStatus.UNCHANGED])
    #assert status.msg == "Incoming file matched hash for last inserted file for pid = 314159. Nothing has been inserted."
    new_records = records_in_file[RecordStatus.NEW]
    modified_records = records_in_file[RecordStatus.MODIFIED]
    unchanged_records = records_in_file[RecordStatus.UNCHANGED]

    print(":)")