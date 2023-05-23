""" Unit tests for the classes used for storing the data. The easiest 
way of doing this seems to just be loading a test files with no child objects. 
"""

import ukrdc_xsdata.ukrdc as xsd_ukrdc
from xsdata.models.datatype import XmlDateTime
import datetime as dt
from xsdata.formats.dataclass.parsers import XmlParser
from ukrdc_cupid.core.store.models import ukrdc as models
from ukrdc_cupid.core.parse.utils import load_xml_from_path
import ukrdc_sqla.ukrdc as sqla


def test_patient_record_xml_mapping():
    """
    To be expanded: this test loads a full xml record 
    """
    xml = load_xml_from_path(r"scripts/xml_examples/UKRDC.xml")

    patient_record = models.PatientRecord(xml)
    patient_record.map_xml_to_tree()

    assert patient_record.orm_object.sendingfacility == "ABC123"
    assert patient_record.orm_object.sendingextract == "UKRDC"

def test_patient():
    """
    test load a patient xml object
    """

    gender = "1" 
    birthtime = dt.datetime(69,6,9)

    xml = XmlParser().from_string(
        f"""<Patient>
	        <Gender>{gender}</Gender>
	        <BirthTime>{XmlDateTime.from_datetime(birthtime)}</BirthTime>
        </Patient>
        """,
        xsd_ukrdc.Patient
    )

    patient = models.Patient(xml)
    assert isinstance(patient.orm_object, sqla.Patient)
    assert patient.xml == xml 

    patient.map_xml_to_tree()
    assert patient.orm_object.gender == gender
    assert patient.orm_object.birthtime == birthtime

    pid = "pidcue"
    patient.transformer(pid)
    assert patient.orm_object.pid == pid

    








