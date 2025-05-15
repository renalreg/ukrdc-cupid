
import os
import copy
import datetime as dt

from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.store.insert import insert_incoming_data

from xsdata.models.datatype import XmlDateTime

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
        is_new=False
    )
    assert status.msg == "Incoming file matched hash for last inserted file for pid = 314159. No further data insertion has occurred."
    assert not status.new_records
    assert not status.unchanged_records 
    assert not status.modified_records 


    # clear out hash - all records unchanged
    patient_record = status.patient_record.orm_object
    patient_record.channelid = None
    ukrdc_test_session.commit()
    status = insert_incoming_data(
        ukrdc_test_session, 
        TEST_PID, 
        TEST_UKRDCID, 
        xml_test, 
        is_new=False,
    )
    assert not status.new_records
    assert status.unchanged_records == 18 
    assert not status.modified_records 

    # clear out hash - extract in ex-missing mode
    # deleted record should not be removed
    patient_record = status.patient_record.orm_object
    patient_record.channelid = None
    ukrdc_test_session.commit()

    # modify xml by removing an observation and modifying the start and stop
    xml_modified = copy.copy(xml_test)
    del xml_modified.observations.observation[0]
    xml_modified.observations.start = XmlDateTime(2006,1,1,0,0,0)
    xml_modified.observations.stop = XmlDateTime(2006,12,1,0,0,0)

    status = insert_incoming_data(
        ukrdc_test_session, 
        TEST_PID, 
        TEST_UKRDCID, 
        xml_modified,
        mode = "ex-missing", 
        is_new=False,
    )
    patient_record = status.patient_record
    

    assert not status.new_records
    assert not status.deleted_records
    assert status.unchanged_records == 17


    # In full update mode the missing record gets removed
    patient_record = status.patient_record.orm_object
    patient_record.channelid = None
    ukrdc_test_session.commit()

    status = insert_incoming_data(
        ukrdc_test_session, 
        TEST_PID, 
        TEST_UKRDCID, 
        xml_modified,
        mode = "full", 
        is_new=False,
    )

    
    assert not status.new_records
    assert status.deleted_records == 1
    assert status.unchanged_records == 17      