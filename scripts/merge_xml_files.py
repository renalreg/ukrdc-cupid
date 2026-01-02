"""
Motivated by  TNG-1286 the motivation behind this script is to generate files
to overwrite existing patients with extra data without deleting the data which
is already in place. This logic is more how I would do the store models in 2026
sans Joel.

git@github.com:renalreg/ukrdc_database.git
"""


import glob
from abc import abstractmethod
from lxml import etree
from ukrdc_cupid.core.match.identify import read_patient_metadata_etree, match_pid
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from dotenv import dotenv_values
from datetime import datetime
from ukrdc_sqla.ukrdc import PatientRecord
from ukrdc.database.models.pyxb_xml import PatientRecord_pyxb_xml
from ukrdc.database.models.pyxb_xml_settings import XmlSettings

# i/o
INPUT_DIR = Path(".xml_to_load") / "xml_in"
OUTPUT_DIR = Path(".xml_to_load")/ "xml_out"
NAMESPACES = {"ukrdc": "http://www.rixg.org.uk/"}

# db connection parameters
env = dotenv_values()

# utility classes to handle xml serialization
class BaseModel:
    def __init__(self, parent_id:str, patient_xml: etree._Element, xpath:str):
        self.parent_id = parent_id
        self.patient_record = patient_xml
        self.xpath = xpath
        self.xml_elements = self.get_elements()
    
    @abstractmethod
    def key_gen(self, element:etree._Element):
        pass

    def get_elements(self):
        # Get the elements themselves, not text nodes which include whitespace
        return self.patient_record.xpath(self.xpath, namespaces=NAMESPACES)

    def serialize_to_dict(self):
        xml_dict = {}
        for element in self.xml_elements:
            key = self.key_gen(element)
            xml_dict[key] = etree.tostring(element)
        return xml_dict

class LabOrder(BaseModel):
    def __init__(self, pid:str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, "LabOrders/LabOrder")
    
    def key_gen(self, lab_order:etree._Element) -> str:
        placer_id = lab_order.find(".//PlacerId")
        return f"{self.parent_id}:{placer_id.text}"
        


class Observation(BaseModel):
    def __init__(self, pid:str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, "Observations/Observation")

    def key_gen(self, observation:etree._Element) -> str:
        
        # Extract observation time and convert to timestamp
        obs_time_elem = observation.find(".//ObservationTime")
        obs_time = datetime.fromisoformat(obs_time_elem.text.replace('Z', '+00:00'))
        time_uts = obs_time.timestamp()
        
        # Extract observation code
        seq_no = 0
        code_elem = observation.find(".//ObservationCode/Code")
        code = code_elem.text
        
        return f"{self.parent_id}:{time_uts}:{code}:{seq_no}"


class DialysisSession(BaseModel):
    def __init__(self, pid:str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, "DialysisSessions/DialysisSession")
    
    def key_gen(self, dialysis_session: etree._Element) -> str:
        # Extract procedure time and convert to timestamp
        procedure_time_elem = dialysis_session.find(".//ProcedureTime")
        procedure_time = datetime.fromisoformat(procedure_time_elem.text.replace('Z', '+00:00'))
        procedure_time_uts = procedure_time.timestamp()
        
        # Extract procedure type code
        procedure_type_elem = dialysis_session.find(".//ProcedureType/Code")
        procedure_type_code = procedure_type_elem.text
        
        seq_no = 0  # hardcode as zero to prevent problems with ex-missing
        return f"{self.parent_id}:{procedure_time_uts}:{procedure_type_code}:{seq_no}"


def serialise_xml_to_dict(pid:str, xml_doc: etree._Element):
    """Extract elements from XML document based on XPATH_MAP."""

    return {
        "lab_order" : LabOrder(pid, xml_doc).serialize_to_dict(),
        "observation" : Observation(pid, xml_doc), 
        "dialysis_session" : DialysisSession(pid, xml_doc)
    }

def get_domain_xml_dump(pid:str, ukrdc_session:Session):
    patient_record = ukrdc_session.execute(
        select(PatientRecord).where(PatientRecord.pid == pid)
    ).scalar_one_or_none()
    xml_settings =  XmlSettings
    xml_settings.full_patient_record = True
    xml_dump = PatientRecord_pyxb_xml(patient_record, xml_settings)
    print(":)")
    return

def merge_xml_dir_with_ukrdc(input_dir:Path, output_dir:Path, ukrdc_session:Session):
    """Function loads a set of xml files containing incomplete information from
    a specified directory and adds them to a dump of an existing patient record
    in the database for reprocessing. 

    TODO: This may be a many to one type deal so it might be helpful to combine
    all incoming files with the domain simultaneously 

    Args:
        input_dir (Path): Directory containing xml files to be merged
        output_dir (Path): Directory to write merged xml files to
        ukrdc_session (Session): SQLAlchemy session to the ukrdc database
    """
    # Parse xml file 
    xml_files = glob.glob(str(input_dir / "*.xml"))

    for xml_path in xml_files:
        with open(xml_path, "r", encoding="utf-8") as file:
            data = file.read()
            xml_doc = etree.XML(data.encode())
            patient_info = read_patient_metadata_etree(xml_doc)
            pid,_,_  = match_pid(ukrdc_session, patient_info)
            incoming_xml_dict = serialise_xml_to_dict(pid, xml_doc)
            domain_xml_doc = etree.XML(get_domain_xml_dump(pid, ukrdc_session))


if __name__ == "__main__":
    
    driver = env["UKRDC_DRIVER"]
    user = env["UKRDC_USER"]
    password = env["UKRDC_PASSWORD"]
    port = env["UKRDC_PORT"]
    name = env["UKRDC_NAME"]
    host = env["UKRDC_HOST"]
    
    db_url = f"{driver}://{user}:{password}@{host}:{port}/{name}"
    engine = create_engine(db_url)
    ukrdc_sessionmaker = sessionmaker(bind=engine)
    with ukrdc_sessionmaker() as ukrdc_session:
        merge_xml_dir_with_ukrdc(INPUT_DIR, OUTPUT_DIR, ukrdc_session)