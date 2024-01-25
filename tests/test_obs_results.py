"""
This file contains the tests for Observations, Results and 
"""

from conftest import create_test_session, TEST_DB_URL
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from typing import Tuple
import ukrdc_xsdata.ukrdc as xsd # type: ignore
import ukrdc_sqla.ukrdc as sqla 
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import pytest

TEST_PID = "test_pid"
TEST_UKRDCID = "test_id"

@pytest.fixture(scope="function")
def ukrdc_test_2():
    """Function creates the database state prior to running cupid. To do this
    we load the generic patient and then add in data that will create the
    behaviour we want to test.  

    Yields:
        Session: session for test database with some data loaded
    """
    xml_test_1 = load_xml_from_path(
        os.path.join("tests","xml_files","store_tests","test_0.xml")
    )

    ukrdc3_session = create_test_session(TEST_DB_URL)
    patient_record = PatientRecord(xml_test_1)  
    patient_record.map_to_database(TEST_PID, TEST_UKRDCID, ukrdc3_session)
    ukrdc3_session.add_all(patient_record.get_orm_list())


    xml_test_2 = load_xml_from_path(
        os.path.join("tests","xml_files","store_tests","test_2.xml")
    )

    lab_order_start = xml_test_2.lab_orders.start.to_datetime()
    lab_order_stop = xml_test_2.lab_orders.stop.to_datetime()

    lab_orders = [
        sqla.LabOrder(
            pid = TEST_PID, 
            id = "to_delete_1",
            specimencollectedtime = lab_order_start + timedelta(weeks=1)
        ),
        sqla.LabOrder(
            pid = TEST_PID, 
            id = "to_persist_1",
            specimencollectedtime = lab_order_start - timedelta(weeks=1)
        ),
        sqla.LabOrder(
            pid = TEST_PID, 
            id = "to_persist_2",
            specimencollectedtime = lab_order_stop + timedelta(weeks=1)
        ),
        sqla.LabOrder(
            pid = TEST_PID, 
            id = f"{TEST_PID}:1",
            specimencollectedtime = lab_order_stop + timedelta(weeks=1)
        )
    ]
    ukrdc3_session.add_all(lab_orders)
    ukrdc3_session.commit()
    
    loaded_ids = [order.id for order in ukrdc3_session.query(sqla.LabOrder).all()]
    for order in lab_orders:
        assert order.id in loaded_ids 

    yield ukrdc3_session

    ukrdc3_session.close()


@pytest.fixture(scope="function")
def patient_record(ukrdc_test_2:Session):
    """Run cupid with test file and produce a set of objects for interogation
    with the unit tests.

    Args:
        ukrdc_test_2 (Session): test database session

    Returns:
        _type_: _description_
    """
    
    xml_test_2 = load_xml_from_path(
        os.path.join("tests","xml_files","store_tests","test_2.xml")
    )
    patient_record = PatientRecord(xml_test_2)
    patient_record.map_to_database(TEST_PID, TEST_UKRDCID, ukrdc_test_2)

    return patient_record

def test_lab_orders(patient_record:Tuple[xsd.PatientRecord,dict]):

    lab_order_orm = False
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "laborder":
            lab_order_orm = orm_object
            break

    assert lab_order_orm
    lab_order_xml = patient_record.xml.lab_orders.lab_order[0]

    # check ids
    assert lab_order_orm.pid == TEST_PID

    # this needs to be checked there is some validation here:
    # https://github.com/renalreg/Data-Repository/blob/52178acad21507678e19c577764f64318aeef896/src/main/java/org/ukrdc/repository/RepositoryManager.java#L1051
    # kind of seems strange the id here isn't the external id
    assert lab_order_orm.id == f"{TEST_PID}:{lab_order_xml.placer_id}"

    # check all the attributes have been mapped over
    assert lab_order_orm.duration == lab_order_xml.duration
    assert lab_order_orm.entered_at == lab_order_xml.entered_at.code
    assert lab_order_orm.entered_on == lab_order_xml.entered_on.to_datetime()
    assert lab_order_orm.enteredon == lab_order_xml.entered_on.to_datetime()
    assert lab_order_orm.external_id == lab_order_xml.external_id
    assert lab_order_orm.externalid == lab_order_xml.external_id
    assert lab_order_orm.filler_id == lab_order_xml.filler_id
    assert lab_order_orm.fillerid == lab_order_xml.filler_id
    assert lab_order_orm.order_category == lab_order_xml.order_category
    assert lab_order_orm.orderitemcode == lab_order_xml.order_item.code
    assert lab_order_orm.orderitemcodestd == lab_order_xml.order_item.coding_standard
    assert lab_order_orm.orderitemdesc == lab_order_xml.order_item.description
    assert lab_order_orm.orderedbycode == lab_order_xml.ordered_by.code
    assert lab_order_orm.orderedbycodestd == lab_order_xml.ordered_by.coding_standard.value
    assert lab_order_orm.orderedbydesc == lab_order_xml.ordered_by.description
    assert lab_order_orm.placer_id == lab_order_xml.placer_id
    assert lab_order_orm.placerid == lab_order_xml.placer_id
    assert lab_order_orm.receivinglocationcode == lab_order_xml.receiving_location.code
    assert lab_order_orm.receivinglocationcodestd == lab_order_xml.receiving_location.coding_standard.value
    assert lab_order_orm.receivinglocationdesc == lab_order_xml.receiving_location.description

    assert lab_order_orm.specimen_collected_time == lab_order_xml.specimen_collected_time.to_datetime()
    assert lab_order_orm.specimen_received_time == lab_order_xml.specimen_received_time.to_datetime()
    assert lab_order_orm.specimen_source == lab_order_xml.specimen_source
    assert lab_order_orm.specimencollectedtime == lab_order_xml.specimen_collected_time.to_datetime()
    assert lab_order_orm.specimenreceivedtime == lab_order_xml.specimen_received_time.to_datetime()
    assert lab_order_orm.specimensource == lab_order_xml.specimen_source
    assert lab_order_orm.status == lab_order_xml.status
    assert lab_order_orm.updatedon == lab_order_xml.updated_on.to_datetime()


def test_laborder_start_stop(patient_record:Tuple[xsd.PatientRecord,dict]):
    # Required behaviour here
    # existing laborders with a observation time within the start stop range should 
    # be removed if they are not in incoming
    
    ids_to_delete = ["to_delete_1"]
    deleted_ids = [orm.id for orm in patient_record.deleted_orm] 
    
    # check the records we expect to delete are staged for deletion
    assert ids_to_delete == deleted_ids