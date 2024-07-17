"""
These tests check that the data which is in the xml gets loaded into the orm
this is the core functionality of CUPID. 
"""


from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.utils import DatabaseConnection
import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import pytest
import uuid

TEST_PID = "test_pid"
TEST_UKRDCID = "test_id"


@pytest.fixture(scope="function")
def ukrdc_test_with_data(ukrdc_test_session: Session):
    """Function creates the database state prior to running cupid. To do this
    we load the generic patient and then add in data that will create the
    behaviour we want to test.

    Yields:
        Session: session for test database with some data loaded
    """
    xml_test_1 = load_xml_from_path(
        os.path.join("tests", "xml_files", "store_tests", "test_0.xml")
    )

    patient_record = PatientRecord(xml_test_1)
    patient_record.map_to_database(TEST_PID, TEST_UKRDCID, ukrdc_test_session)
    ukrdc_test_session.add_all(patient_record.get_orm_list())

    xml_test_2 = load_xml_from_path(
        os.path.join("tests", "xml_files", "store_tests", "test_2.xml")
    )

    lab_order_start = xml_test_2.lab_orders.start.to_datetime()
    lab_order_stop = xml_test_2.lab_orders.stop.to_datetime()

    lab_orders = [
        sqla.LabOrder(
            pid=TEST_PID,
            id="to_delete_1",
            specimencollectedtime=lab_order_start + timedelta(weeks=1),
        ),
        sqla.LabOrder(
            pid=TEST_PID,
            id="to_persist_1",
            specimencollectedtime=lab_order_start - timedelta(weeks=1),
        ),
        sqla.LabOrder(
            pid=TEST_PID,
            id="to_persist_2",
            specimencollectedtime=lab_order_stop + timedelta(weeks=1),
        ),
        sqla.LabOrder(
            pid=TEST_PID,
            id=f"{TEST_PID}:1",
            specimencollectedtime=lab_order_stop + timedelta(weeks=1),
        ),
    ]
    ukrdc_test_session.add_all(lab_orders)

    result_items = [
        sqla.ResultItem(id="RI_to_delete_1", order_id="to_delete_1"),
    ]
    ukrdc_test_session.add_all(result_items)
    ukrdc_test_session.commit()

    loaded_ids = [order.id for order in ukrdc_test_session.query(sqla.LabOrder).all()]
    for order in lab_orders:
        assert order.id in loaded_ids

    return ukrdc_test_session


@pytest.fixture(scope="function")
def patient_record(ukrdc_test_with_data: Session):
    """Run cupid with test file and produce a set of objects for interogation
    with the unit tests.

    Args:
        ukrdc_test_with_data (Session): test database session

    Returns:
        _type_: _description_
    """

    xml_test_2 = load_xml_from_path(
        os.path.join("tests", "xml_files", "store_tests", "test_2.xml")
    )
    patient_record = PatientRecord(xml_test_2)
    patient_record.map_to_database(TEST_PID, TEST_UKRDCID, ukrdc_test_with_data)

    return patient_record


def test_lab_orders(patient_record: PatientRecord):

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


def test_laborder_start_stop(patient_record: PatientRecord):
    # Required behaviour here
    # existing laborders with a observation time within the start stop range
    # should be removed if they are not in incoming any associated result items
    # should staged for deletion

    ids_to_delete = ["to_delete_1", "RI_to_delete_1"]
    deleted_ids = [orm.id for orm in patient_record.deleted_orm]

    # check the records we expect to delete are staged for deletion
    assert ids_to_delete == deleted_ids


def test_result_items(patient_record: PatientRecord):
    # check all the result item attributes are being loaded into the orm
    result_orms = []
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "resultitem":
            result_orms.append(orm_object)

    assert result_orms

    results_xml = patient_record.xml.lab_orders.lab_order[0].result_items.result_item
    for result_orm, result_xml in zip(result_orms, results_xml):
        assert result_orm.resulttype == result_xml.result_type
        assert result_orm.enteredon == result_xml.entered_on.to_datetime()
        assert result_orm.prepost == result_xml.pre_post.value
        assert result_orm.serviceidcode == result_xml.service_id.code
        assert result_orm.serviceiddesc == result_xml.service_id.description
        assert (
            result_orm.serviceidcodestd == result_xml.service_id.coding_standard.value
        )
        assert result_orm.subid == result_xml.sub_id
        assert result_orm.resultvalue == result_xml.result_value
        assert result_orm.resultvalueunits == result_xml.result_value_units
        assert result_orm.referencerange == result_xml.reference_range
        assert result_orm.interpretationcodes == result_xml.interpretation_codes
        assert result_orm.status == result_xml.status
        assert result_orm.observationtime == result_xml.observation_time.to_datetime()
        assert result_orm.commenttext == result_xml.comments
        assert result_orm.referencecomment == result_xml.reference_comment


def test_dialysis_session(patient_record: PatientRecord):

    dialysis_session_orms = []
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "dialysissession":
            dialysis_session_orms.append(orm_object)

    assert dialysis_session_orms
    xml = patient_record.xml.procedures.dialysis_sessions[0].dialysis_session

    for dialysis_session_orm, dialysis_xml in zip(dialysis_session_orms, xml):
        assert dialysis_session_orm.enteredatcode == dialysis_xml.entered_at.code
        assert (
            dialysis_session_orm.enteredatcodestd
            == dialysis_xml.entered_at.coding_standard.value
        )
        assert dialysis_session_orm.enteredatdesc == dialysis_xml.entered_at.description

        # times
        assert (
            dialysis_session_orm.proceduretime
            == dialysis_xml.procedure_time.to_datetime()
        )
        assert dialysis_session_orm.updatedon == dialysis_xml.updated_on.to_datetime()
        assert dialysis_session_orm.externalid == dialysis_xml.external_id

        # values
        assert dialysis_session_orm.qhd19 == dialysis_xml.symtomatic_hypotension
        if dialysis_xml.vascular_access:
            assert dialysis_session_orm.qhd20 == dialysis_xml.vascular_access.code
        if dialysis_xml.vascular_access_site:
            assert dialysis_session_orm.qhd21 == dialysis_xml.vascular_access_site.code
        assert dialysis_session_orm.qhd31 == dialysis_xml.time_dialysed


def test_procedure(patient_record: PatientRecord):
    # This is a bit of a non table
    assert True


def test_vascular_access(patient_record: PatientRecord):
    vascular_access_orms = []
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "vascularaccess":
            vascular_access_orms.append(orm_object)

    assert vascular_access_orms
    xml = patient_record.xml.procedures.vascular_access
    for vascular_orm, vascular_xml in zip(vascular_access_orms, xml):
        assert vascular_orm.proceduretypecode == vascular_xml.procedure_type.code
        assert vascular_orm.proceduretypecodestd == vascular_xml.procedure_type.coding_standard.value
        assert vascular_orm.proceduretypedesc == vascular_xml.procedure_type.description
        assert vascular_orm.proceduretime == vascular_xml.procedure_time.to_datetime()
        assert vascular_orm.enteredatcode == vascular_xml.entered_at.code
        assert vascular_orm.enteredatcodestd == vascular_xml.entered_at.coding_standard.value
        assert vascular_orm.enteredatdesc == vascular_xml.entered_at.description
        assert vascular_orm.acc19 == vascular_xml.attributes.acc19.to_datetime()
        assert vascular_orm.acc20 == vascular_xml.attributes.acc20.to_datetime()
        assert vascular_orm.acc21 == vascular_xml.attributes.acc21.to_datetime()
        assert vascular_orm.acc22 == vascular_xml.attributes.acc22
        assert vascular_orm.acc30 == vascular_xml.attributes.acc30.value
        assert vascular_orm.acc40 == vascular_xml.attributes.acc40


def test_transplant(patient_record: PatientRecord):
    transplant_orms = []
    orm_objects = patient_record.get_orm_list()
    for orm_object in orm_objects:
        if orm_object.__tablename__ == "transplant":
            transplant_orms.append(orm_object)
    assert transplant_orms

    xml = patient_record.xml.procedures.transplant

    for transplant_orm, transplant_xml in zip(transplant_orms, xml):
        # ProcedureType
        assert transplant_orm.proceduretypecode == transplant_xml.procedure_type.code
        assert transplant_orm.proceduretypecodestd == transplant_xml.procedure_type.coding_standard.value
        assert transplant_orm.proceduretypedesc == transplant_xml.procedure_type.description

        # ProcedureTime
        assert transplant_orm.proceduretime == transplant_xml.procedure_time.to_datetime()

        # EnteredAt
        assert transplant_orm.enteredatcode == transplant_xml.entered_at.code
        assert transplant_orm.enteredatcodestd == transplant_xml.entered_at.coding_standard.value
        assert transplant_orm.enteredatdesc == transplant_xml.entered_at.description

        # Optional fields
        if transplant_xml.updated_on:
            assert transplant_orm.updatedon == transplant_xml.updated_on.to_datetime()
        if transplant_xml.external_id:
            assert transplant_orm.externalid == transplant_xml.external_id

        # Former attributes
        assert transplant_orm.tra77 == transplant_xml.donor_type.value
        #assert transplant_orm.tra72 == transplant_xml.date_registered.to_date()
        assert transplant_orm.tra64 == transplant_xml.failure_date.to_datetime()
        assert transplant_orm.tra91 == transplant_xml.cold_ischaemic_time
        assert transplant_orm.tra83 == transplant_xml.hlamismatch_a
        assert transplant_orm.tra84 == transplant_xml.hlamismatch_b
        assert transplant_orm.tra85 == transplant_xml.hlamismatch_c


def test_treatment(patient_record: PatientRecord):
    treatment_orms = []
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "treatment":
            treatment_orms.append(orm_object)

    assert treatment_orms
    treatment_xml = patient_record.xml.encounters.treatment[0]

    xml = patient_record.xml.encounters.treatment

    for orm_object, treatment_xml in zip(treatment_orms, xml):
        assert orm_object.encounternumber == treatment_xml.encounter_number
        if treatment_xml.admitting_clinician:
            assert orm_object.admittingcliniciancode == treatment_xml.admitting_clinician.code
            if treatment_xml.admitting_clinician.coding_standard:
                assert orm_object.admittingcliniciancodestd == treatment_xml.admitting_clinician.coding_standard.value
        
            assert orm_object.admittingcliniciandesc == treatment_xml.admitting_clinician.description
            

        if treatment_xml.admit_reason:
            assert orm_object.admitreasoncode == treatment_xml.admit_reason.code.value
            if treatment_xml.admit_reason.coding_standard:
                assert orm_object.admitreasoncodestd == treatment_xml.admit_reason.coding_standard.value
            assert orm_object.admitreasondesc == treatment_xml.admit_reason.description

        if treatment_xml.admission_source:
            assert orm_object.admissionsourcecode == treatment_xml.admission_source.code
            if treatment_xml.admission_source.coding_standard:
                assert orm_object.admissionsourcecodestd == treatment_xml.admission_source.coding_standard.value
            # assert orm_object.admissionsourcedesc == treatment_xml.admission_source.code.description

        if treatment_xml.discharge_reason:
            assert orm_object.dischargereasoncode == treatment_xml.discharge_reason.code.value
            if treatment_xml.discharge_reason.coding_standard:
                assert orm_object.dischargereasoncodestd == treatment_xml.discharge_reason.coding_standard.value
            assert orm_object.dischargereasondesc == treatment_xml.discharge_reason.description

        if treatment_xml.discharge_location:
            assert orm_object.dischargelocationcode == treatment_xml.discharge_location.code
            if treatment_xml.discharge_location.coding_standard:
                assert orm_object.dischargelocationcodestd == treatment_xml.discharge_location.coding_standard.value
            assert orm_object.dischargelocationdesc == treatment_xml.discharge_location.description

        if treatment_xml.health_care_facility:
            assert orm_object.healthcarefacilitycode == treatment_xml.health_care_facility.code
    
            if treatment_xml.health_care_facility.coding_standard:
                assert orm_object.healthcarefacilitycodestd == treatment_xml.health_care_facility.coding_standard.value
            assert orm_object.healthcarefacilitydesc == treatment_xml.health_care_facility.description

        if treatment_xml.entered_at:
            assert orm_object.enteredatcode == treatment_xml.entered_at.code
            if treatment_xml.entered_at.coding_standard:
                assert orm_object.enteredatcodestd == treatment_xml.entered_at.coding_standard.value
            assert orm_object.enteredatdesc == treatment_xml.entered_at.description

        assert orm_object.visitdescription == treatment_xml.visit_description
        # assert orm_object.qbl05 == treatment_xml.qbl05

def test_transplant_list(patient_record: PatientRecord):
    transplant_list_orms = []
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "transplantlist":
            transplant_list_orms.append(orm_object)

    assert transplant_list_orms
    transplant_xml_list = patient_record.xml.encounters.transplant_list

    for orm_object, transplant_xml in zip(transplant_list_orms, transplant_xml_list):
        assert orm_object.encounternumber == transplant_xml.encounter_number
        assert orm_object.encountertype == transplant_xml.encounter_type.value
        assert orm_object.fromtime == transplant_xml.from_time.to_datetime()
        assert orm_object.totime == transplant_xml.to_time.to_datetime()

        if transplant_xml.admitting_clinician:
            assert (orm_object.admittingcliniciancode== transplant_xml.admitting_clinician.code)
            if transplant_xml.admitting_clinician.coding_standard:
                assert (orm_object.admittingcliniciancodestd == transplant_xml.admitting_clinician.coding_standard.value)
            assert (orm_object.admittingcliniciandesc == transplant_xml.admitting_clinician.description)

        if transplant_xml.admit_reason:
            assert orm_object.admitreasoncode == transplant_xml.admit_reason.code
            if transplant_xml.admit_reason.coding_standard:
                assert (orm_object.admitreasoncodestd == transplant_xml.admit_reason.coding_standard)
            assert orm_object.admitreasondesc == transplant_xml.admit_reason.description

        if transplant_xml.admission_source:
            assert orm_object.admissionsourcecode == transplant_xml.admission_source.code
            if transplant_xml.admission_source.coding_standard:
                assert (orm_object.admissionsourcecodestd == transplant_xml.admission_source.coding_standard.value)
            assert orm_object.admissionsourcedesc == transplant_xml.admission_source.description

        if transplant_xml.discharge_reason:
            assert (orm_object.dischargereasoncode== transplant_xml.discharge_reason.code)
            if transplant_xml.discharge_reason.coding_standard:
                assert (orm_object.dischargereasoncodestd == transplant_xml.discharge_reason.coding_standard)
            assert (orm_object.dischargereasondesc == transplant_xml.discharge_reason.description)

        if transplant_xml.discharge_location:
            assert (orm_object.dischargelocationcode == transplant_xml.discharge_location.code)
            if transplant_xml.discharge_location.coding_standard:
                assert (orm_object.dischargelocationcodestd== transplant_xml.discharge_location.coding_standard.value)
            assert (orm_object.dischargelocationdesc == transplant_xml.discharge_location.description)

        if transplant_xml.health_care_facility:
            assert orm_object.healthcarefacilitycode == transplant_xml.health_care_facility.code
            if transplant_xml.health_care_facility.coding_standard:
                assert orm_object.healthcarefacilitycodestd == transplant_xml.health_care_facility.coding_standard.value
            assert orm_object.healthcarefacilitydesc == transplant_xml.health_care_facility.description

        if transplant_xml.entered_at:
            assert orm_object.enteredatcode == transplant_xml.entered_at.code
            if transplant_xml.entered_at.coding_standard:
                assert orm_object.enteredatcodestd == transplant_xml.entered_at.coding_standard.value
            assert orm_object.enteredatdesc == transplant_xml.entered_at.description

        assert orm_object.visitdescription == transplant_xml.visit_description

        if transplant_xml.updated_on:
            assert orm_object.updatedon == transplant_xml.updated_on.to_datetime()
        if transplant_xml.external_id:
            assert orm_object.externalid == transplant_xml.external_id

def test_encounter(patient_record: PatientRecord):
    encounter_orms = []
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "encounter":
            encounter_orms.append(orm_object)
    
    assert encounter_orms

    assert True