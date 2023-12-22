"""
This is to test the bits of the record which aren't sent in full.
"""

from conftest import ukrdc3_session
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from typing import Tuple
import ukrdc_xsdata.ukrdc as xsd # type: ignore
import os
import pytest
import inspect

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

def test_lab_orders(test_patient_objects:Tuple[xsd.PatientRecord,dict]):
    patient_record_xml, orms = test_patient_objects
    lab_order_xml = patient_record_xml.lab_orders.lab_order[0]
    lab_order = orms["laborder"][0]
    #lab_order_keys = [item for item in dir(lab_order_xml)]
    #for attr, _ in inspect.getmembers(lab_order):
    #    for xml_attr in lab_order_keys:
    #        if attr.replace("_","") == xml_attr.replace("_",""):
    #            print(f"assert lab_order.{attr} == lab_order_xml.{xml_attr}")


    # check ids
    assert lab_order.pid == TEST_PID

    # this needs to be checked there is some validation here:
    # https://github.com/renalreg/Data-Repository/blob/52178acad21507678e19c577764f64318aeef896/src/main/java/org/ukrdc/repository/RepositoryManager.java#L1051
    # kind of seems strange the id here isn't the external id
    assert lab_order.id == f"{TEST_PID}:{lab_order_xml.placer_id}"

    # check all the attributes have been mapped over
    assert lab_order.duration == lab_order_xml.duration
    assert lab_order.entered_at == lab_order_xml.entered_at.code
    assert lab_order.entered_on == lab_order_xml.entered_on.to_datetime()
    assert lab_order.enteredon == lab_order_xml.entered_on.to_datetime()
    assert lab_order.external_id == lab_order_xml.external_id
    assert lab_order.externalid == lab_order_xml.external_id
    assert lab_order.filler_id == lab_order_xml.filler_id
    assert lab_order.fillerid == lab_order_xml.filler_id
    assert lab_order.order_category == lab_order_xml.order_category
    assert lab_order.orderitemcode == lab_order_xml.order_item.code
    assert lab_order.orderitemcodestd == lab_order_xml.order_item.coding_standard
    assert lab_order.orderitemdesc == lab_order_xml.order_item.description
    assert lab_order.orderedbycode == lab_order_xml.ordered_by.code
    assert lab_order.orderedbycodestd == lab_order_xml.ordered_by.coding_standard.value
    assert lab_order.orderedbydesc == lab_order_xml.ordered_by.description
    assert lab_order.placer_id == lab_order_xml.placer_id
    assert lab_order.placerid == lab_order_xml.placer_id
    #assert lab_order.prioritycode == lab_order_xml.priority.code
    #assert lab_order.prioritycodestd == lab_order_xml.priority.coding_standard
    #assert lab_order.prioritydesc == lab_order_xml.priority.description
    assert lab_order.receivinglocationcode == lab_order_xml.receiving_location.code
    assert lab_order.receivinglocationcodestd == lab_order_xml.receiving_location.coding_standard.value
    assert lab_order.receivinglocationdesc == lab_order_xml.receiving_location.description

    assert lab_order.specimen_collected_time == lab_order_xml.specimen_collected_time.to_datetime()
    assert lab_order.specimen_received_time == lab_order_xml.specimen_received_time.to_datetime()
    assert lab_order.specimen_source == lab_order_xml.specimen_source
    assert lab_order.specimencollectedtime == lab_order_xml.specimen_collected_time.to_datetime()
    assert lab_order.specimenreceivedtime == lab_order_xml.specimen_received_time.to_datetime()
    assert lab_order.specimensource == lab_order_xml.specimen_source
    assert lab_order.status == lab_order_xml.status
    assert lab_order.updatedon == lab_order_xml.updated_on.to_datetime()