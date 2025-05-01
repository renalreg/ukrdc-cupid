from sqlalchemy.orm import Session
from ukrdc_cupid.core.store.models.structure import Node, RecordStatus
from xsdata.models.datatype import XmlDateTime
from datetime import datetime
import ukrdc_sqla.ukrdc as sqla
import ukrdc_xsdata.ukrdc as xsd_ukrdc
import ukrdc_xsdata.ukrdc.types as xsd_types

import pytest


# Partial sample of Nodes to be static for testing
class Patient(Node):
    def __init__(self, xml: xsd_ukrdc.Patient):
        super().__init__(xml, sqla.Patient)

    def sqla_mapped() -> None:
        return None

    def map_xml_to_orm(self, _) -> None:
        return

    def map_to_database(self) -> None:
        # id = self.generate_id()
        self.pid = "test_pid"
        # self.orm_object = self.orm_model(id=id)
        self.orm_object = self.orm_model()
        return id


class PatientNumber(Node):
    def __init__(self, xml: xsd_types.PatientNumber):
        super().__init__(xml, sqla.PatientNumber)

    def sqla_mapped() -> str:
        return "numbers"

    def map_xml_to_orm(self, _) -> None:
        self.add_item("patientid", self.xml.number)
        self.add_item("organization", self.xml.organization)
        self.add_item("numbertype", self.xml.number_type)


# set up patient node
@pytest.fixture(scope="function")
def patient_node():
    patient_xml = xsd_ukrdc.Patient(
        patient_numbers=[
            xsd_types.PatientNumbers(
                [
                    xsd_types.PatientNumber(
                        number="AAA111C", organization="LOCALHOSP", number_type="MRN"
                    ),
                    xsd_types.PatientNumber(
                        number="1111111111", organization="NHS", number_type="NI"
                    ),
                ]
            )
        ]
    )

    patient_node = Patient(patient_xml)
    patient_node.map_to_database()

    return patient_node


def test_generate_id(patient_node: Node):
    # do we want to handle the case when self.pid = None more carefully
    seq_no = 0
    id = patient_node.generate_id(seq_no)
    assert id == "test_pid:0"


def test_add_code(patient_node: Node):
    property_code = "123"
    property_std = "XYZ"
    property_description = "Test"
    xml_code = xsd_types.CodedField(
        code=property_code,
        coding_standard=property_std,
        description=property_description,
    )

    patient_node.add_code(
        "ethnicgroupcode", "ethnicgroupcodestd", "ethnicgroupdesc", xml_code
    )

    assert patient_node.orm_object.ethnicgroupcode == property_code
    assert patient_node.orm_object.ethnicgroupcodestd == property_std
    assert patient_node.orm_object.ethnicgroupdesc == property_description

    patient_node.add_code(
        "ethnicgroupcode", "ethnicgroupcodestd", "ethnicgroupdesc", None
    )
    assert patient_node.orm_object.ethnicgroupcode is None
    assert patient_node.orm_object.ethnicgroupcodestd is None
    assert patient_node.orm_object.ethnicgroupdesc is None


def test_add_item(patient_node: Node):
    # TODO: revist all of this timezone stuff
    dod = XmlDateTime.from_string("1984-10-06T00:00:00+00:00")
    dod_datetime = datetime(1984, 10, 6, 1)
    patient_node.add_item("deathtime", dod)
    assert patient_node.status == RecordStatus.MODIFIED
    assert patient_node.orm_object.deathtime.date() == dod_datetime.date()


    # Check nothing changes when we repeat the process
    patient_node.status = RecordStatus.UNCHANGED
    patient_node.orm_object.deathtime = dod_datetime
    patient_node.add_item("deathtime", dod)
    assert patient_node.status == RecordStatus.UNCHANGED



@pytest.mark.parametrize("seq_no", [0, 1])
def test_add_children(ukrdc_test_session: Session, patient_node: Node, seq_no: int):
    # test parsing of xml attributes accross a couple of levels
    patient_node.add_children(
        PatientNumber, "patient_numbers.patient_number", ukrdc_test_session
    )

    # test parsing on single level
    node = patient_node.mapped_classes[seq_no]
    assert isinstance(node, PatientNumber)
    assert isinstance(node.orm_object, sqla.PatientNumber)
