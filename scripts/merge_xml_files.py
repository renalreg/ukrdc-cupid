"""
Motivated by  TNG-1286 the motivation behind this script is to generate files
to overwrite existing patients with extra data without deleting the data which
is already in place. This logic is more how I would do the store models in 2026
sans Joel.

The following will need to be installed to make it work:
git@github.com:renalreg/ukrdc_database.git
"""


import glob
from enum import Enum
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
    
    def key_gen(self, element:etree._Element, idx:str):
        element = element
        return f"{self.parent_id}:{idx}"

    def get_elements(self):
        # Get the elements themselves, not text nodes which include whitespace
        return self.patient_record.xpath(self.xpath, namespaces=NAMESPACES)

    def serialize_to_dict(self):
        xml_dict = {}
        for idx,element in enumerate(self.xml_elements):
            key = self.key_gen(element, idx)
            xml_dict[key] = etree.tostring(element)
        return xml_dict


class LabOrder(BaseModel):
    XPATH = "LabOrders/LabOrder"
    
    def __init__(self, pid:str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)
    
    def key_gen(self, lab_order:etree._Element,_) -> str:
        placer_id = lab_order.find(".//PlacerId")
        return f"{self.parent_id}:{placer_id.text}"


class Observation(BaseModel):
    XPATH = "Observations/Observation"
    
    def __init__(self, pid:str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)

    def key_gen(self, observation:etree._Element,idx:str) -> str:
        
        # Extract observation time and convert to timestamp
        obs_time_elem = observation.find(".//ObservationTime")
        obs_time = datetime.fromisoformat(obs_time_elem.text.replace('Z', '+00:00'))
        time_uts = obs_time.timestamp()
        
        # Extract observation code and hardcode idx
        idx = 0
        code_elem = observation.find(".//ObservationCode/Code")
        code = code_elem.text
        
        return f"{self.parent_id}:{time_uts}:{code}:{idx}"


class DialysisSession(BaseModel):
    XPATH = "DialysisSessions/DialysisSession"
    
    def __init__(self, pid:str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)
    
    def key_gen(self, dialysis_session: etree._Element,idx:str) -> str:
        # Extract procedure time and convert to timestamp
        procedure_time_elem = dialysis_session.find(".//ProcedureTime")
        procedure_time = datetime.fromisoformat(procedure_time_elem.text.replace('Z', '+00:00'))
        procedure_time_uts = procedure_time.timestamp()
        
        # Extract procedure type code
        procedure_type_elem = dialysis_session.find(".//ProcedureType/Code")
        procedure_type_code = procedure_type_elem.text
        
        # Hardcode to zero for now
        idx = 0  
        return f"{self.parent_id}:{procedure_time_uts}:{procedure_type_code}:{idx}"


class Patient(BaseModel):
    XPATH = "Patient"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class SocialHistory(BaseModel):
    XPATH = "SocialHistories/SocialHistory"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class FamilyHistory(BaseModel):
    XPATH = "FamilyHistories/FamilyHistory"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class Allergy(BaseModel):
    XPATH = "Allergies/Allergy"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class Diagnosis(BaseModel):
    XPATH = "Diagnoses/Diagnosis"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class CauseOfDeath(BaseModel):
    XPATH = "CauseOfDeath"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class RenalDiagnosis(BaseModel):
    XPATH = "RenalDiagnoses/RenalDiagnosis"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class Medication(BaseModel):
    XPATH = "Medications/Medication"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class VascularAccess(BaseModel):
    XPATH = "VascularAccesses/VascularAccess"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class Procedure(BaseModel):
    XPATH = "Procedures/Procedure"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class Document(BaseModel):
    XPATH = "Documents/Document"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class Encounter(BaseModel):
    XPATH = "Encounters/Encounter"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class TransplantList(BaseModel):
    XPATH = "TransplantList"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class Treatment(BaseModel):
    XPATH = "Treatments/Treatment"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class ProgramMembership(BaseModel):
    XPATH = "ProgramMemberships/ProgramMembership"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class Transplant(BaseModel):
    XPATH = "Transplants/Transplant"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class OptOut(BaseModel):
    XPATH = "OptOuts/OptOut"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class ClinicalRelationship(BaseModel):
    XPATH = "ClinicalRelationships/ClinicalRelationship"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class Survey(BaseModel):
    XPATH = "Surveys/Survey"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


class PVData(BaseModel):
    XPATH = "PVData"
    
    def __init__(self, pid: str, patient_xml: etree._Element):
        super().__init__(pid, patient_xml, self.XPATH)


XML_CONFIG = {
    "patient": {"model": Patient, "include_domain": True, "include_incoming": False},
    "lab_order": {"model": LabOrder, "include_domain": True, "include_incoming": True},
    "dialysis_session": {"model": DialysisSession, "include_domain": True, "include_incoming": True},
    "observation": {"model": Observation, "include_domain": True, "include_incoming": True},
    "social_history": {"model": SocialHistory, "include_domain": True, "include_incoming": False},
    "family_history": {"model": FamilyHistory, "include_domain": True, "include_incoming": False},
    "allergy": {"model": Allergy, "include_domain": True, "include_incoming": False},
    "diagnosis": {"model": Diagnosis, "include_domain": True, "include_incoming": False},
    "cause_of_death": {"model": CauseOfDeath, "include_domain": True, "include_incoming": False},
    "renal_diagnosis": {"model": RenalDiagnosis, "include_domain": True, "include_incoming": False},
    "medication": {"model": Medication, "include_domain": True, "include_incoming": False},
    "vascular_access": {"model": VascularAccess, "include_domain": True, "include_incoming": False},
    "procedure": {"model": Procedure, "include_domain": True, "include_incoming": False},
    "document": {"model": Document, "include_domain": True, "include_incoming": False},
    "encounter": {"model": Encounter, "include_domain": True, "include_incoming": False},
    "transplant_list": {"model": TransplantList, "include_domain": True, "include_incoming": False},
    "treatment": {"model": Treatment, "include_domain": True, "include_incoming": False},
    "program_membership": {"model": ProgramMembership, "include_domain": True, "include_incoming": False},
    "transplant": {"model": Transplant, "include_domain": True, "include_incoming": False},
    "opt_out": {"model": OptOut, "include_domain": True, "include_incoming": False},
    "clinical_relationship": {"model": ClinicalRelationship, "include_domain": True, "include_incoming": False},
    "survey": {"model": Survey, "include_domain": True, "include_incoming": False},
    "pvdata": {"model": PVData, "include_domain": True, "include_incoming": False},
}


class XmlSource(Enum):
    INCOMING = "incoming"
    DOMAIN = "domain"

def serialise_xml_to_dict(pid: str, xml_doc: etree._Element, source: XmlSource = XmlSource.INCOMING) -> dict:
    """Extract elements from XML document and serialize based on source type.
    
    Args:
        pid: Patient identifier
        xml_doc: XML document element
        source: Source type (INCOMING or DOMAIN)
    
    Returns:
        Dictionary of serialized XML elements
    """
    result = {}
    
    for key, config in XML_CONFIG.items():
        match source:
            case XmlSource.INCOMING:
                if config["include_incoming"]:
                    model_instance = config["model"](pid, xml_doc)
                    result[key] = model_instance.serialize_to_dict()
            case XmlSource.DOMAIN:
                if config["include_domain"]:
                    model_instance = config["model"](pid, xml_doc)
                    result[key] = model_instance.serialize_to_dict()
    
    return result 

def deserialise_xml_dict(domain_file:etree._Element,xml_dict:dict)->etree._Element:
    """Takes the domain xml file and assembles the content based on the
    dictionary containing the merged xml contents.

    Args:
        domain_file (etree._Element): xml generated from the database
        xml_dict (dict): dictionary containing elements to insert into the file 
    """

    root = etree.fromstring(etree.tostring(domain_file))
    for table, config in XML_CONFIG.items():
        elements_to_add = xml_dict[table]
        xpath = config["model"].XPATH

        # Use xpath() not search(), and handle the namespace
        matches = root.xpath(f"//{xpath}", namespaces=NAMESPACES)
        if matches:
            parent = matches[0].getparent()
            # Get the position of the first match before removing
            insert_position = list(parent).index(matches[0])
            # Remove all existing child elements
            for match in matches:
                parent.remove(match)
            # Add the new elements at the original position
            for idx, (_, xml) in enumerate(elements_to_add.items()):
                xml_element = etree.fromstring(xml)
                parent.insert(insert_position + idx, xml_element)

    return root

def deserialise_xml_dict_ai_junk(domain_file:etree._Element, xml_dict:dict) -> etree._Element:
    """Takes the domain xml file and assembles the content based on the
    dictionary containing the merged xml contents.

    Args:
        domain_file (etree._Element): xml generated from the database
        xml_dict (dict): dictionary containing elements to insert into the file 
    
    Returns:
        etree._Element: Reconstructed XML with merged content
    """
    # Map table names to their container element names in the XML
    containers = {
        "lab_order": "LabOrders",
        "observation": "Observations",
        "dialysis_session": "DialysisSessions",
        "social_history": "SocialHistories",
        "family_history": "FamilyHistories",
        "allergy": "Allergies",
        "diagnosis": "Diagnoses",
        "renal_diagnosis": "RenalDiagnoses",
        "medication": "Medications",
        "vascular_access": "VascularAccesses",
        "procedure": "Procedures",
        "document": "Documents",
        "encounter": "Encounters",
        "treatment": "Treatments",
        "program_membership": "ProgramMemberships",
        "transplant": "Transplants",
        "opt_out": "OptOuts",
        "clinical_relationship": "ClinicalRelationships",
        "survey": "Surveys",
    }
    
    # Make a copy of the domain file to avoid mutating the original
    root = etree.fromstring(etree.tostring(domain_file))
    
    for table_name, elements_dict in xml_dict.items():
        if not elements_dict:
            continue
        
        # Get the container name or use the table name directly for root-level elements
        container_name = containers.get(table_name)
        
        if container_name:
            # Find or create the container element
            container_xpath = f".//{{http://www.rixg.org.uk/}}{container_name}"
            container = root.find(container_xpath)
            
            if container is None:
                # Create container if it doesn't exist
                container = etree.SubElement(
                    root,
                    f"{{http://www.rixg.org.uk/}}{container_name}"
                )
            else:
                # Clear existing children from the container
                container.clear()
            
            # Add all elements from the merged dictionary
            for key, xml_bytes in elements_dict.items():
                element = etree.fromstring(xml_bytes)
                container.append(element)
        else:
            # Handle root-level elements (Patient, CauseOfDeath, TransplantList, PVData)
            # Map table names to their element names
            element_names = {
                "patient": "Patient",
                "cause_of_death": "CauseOfDeath",
                "transplant_list": "TransplantList",
                "pvdata": "PVData",
            }
            
            element_name = element_names.get(table_name)
            if element_name:
                # Remove existing element if present
                existing = root.find(f".//{{http://www.rixg.org.uk/}}{element_name}")
                if existing is not None:
                    root.remove(existing)
                
                # Add the new element(s)
                for key, xml_bytes in elements_dict.items():
                    element = etree.fromstring(xml_bytes)
                    root.append(element)
    
    return root

def get_domain_xml_dump(pid:str, ukrdc_session:Session):
    patient_record = ukrdc_session.execute(
        select(PatientRecord).where(PatientRecord.pid == pid)
    ).scalar_one_or_none()

    xml_dump = PatientRecord_pyxb_xml(patient_record, XmlSettings())

    return xml_dump.toxml(encoding="utf-8")

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
            
            # convert the xml to a format which allows comparison between content
            incoming_xml_dict = serialise_xml_to_dict(pid, xml_doc)
            domain_xml_doc = etree.XML(get_domain_xml_dump(pid, ukrdc_session))
            domain_xml_dict = serialise_xml_to_dict(pid, domain_xml_doc, XmlSource.DOMAIN)

            # merge files by appending anything missing in the domain record
            # from incoming
            merged_file = {}
            for table, config in XML_CONFIG.items():
                records = {}
                if config["include_domain"] == True:
                    records = domain_xml_dict.get(table, {})

                if config["include_incoming"] == True:
                    incoming_records = incoming_xml_dict.get(table, {})
                    for key, value in incoming_records.items():
                        if key not in records.keys():
                            records[key] = value
                
                merged_file[table] = records

        # Write domain XML to output directory for comparison
        domain_output_path = output_dir / f"{Path(xml_path).stem}_domain.xml"
        with open(domain_output_path, "wb") as f:
            f.write(etree.tostring(domain_xml_doc, encoding="utf-8", xml_declaration=True, pretty_print=True))
   

        # deserialse back to xml and write to output directory
        merged_doc = deserialise_xml_dict(domain_xml_doc,merged_file)
        output_path = output_dir / f"{Path(xml_path).stem}_merged.xml"
        with open(output_path, "wb") as f:
            f.write(etree.tostring(merged_doc, encoding="utf-8", xml_declaration=True, pretty_print=True))

    return


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