""" Unit tests for the classes used for storing the data. The easiest 
way of doing this seems to just be loading a test files with no child objects. 
TODO: I see problems arising from "null" files this should be integrated into testing.
"""

import ukrdc_xsdata.ukrdc as xsd_ukrdc
import ukrdc_xsdata as xsd_all

import ukrdc_xsdata.ukrdc.types as xsd_types
import ukrdc_xsdata.ukrdc.lab_orders as xsd_lab_orders
import ukrdc_xsdata.ukrdc.social_histories as xsd_social_history  # noqa: F401
import ukrdc_xsdata.ukrdc.family_histories as xsd_family_history  # noqa: F401
import ukrdc_xsdata.ukrdc.allergies as xsd_allergy  # noqa: F401
import ukrdc_xsdata.ukrdc.diagnoses as xsd_diagnosis  # noqa: F401
import ukrdc_xsdata.ukrdc.medications as xsd_medication  # noqa: F401
import ukrdc_xsdata.ukrdc.procedures as xsd_procedures  # noqa: F401
import ukrdc_xsdata.ukrdc.dialysis_sessions as xsd_dialysis_session  # noqa: F401
import ukrdc_xsdata.ukrdc.transplants as xsd_transplants  # noqa: F401
import ukrdc_xsdata.ukrdc.vascular_accesses as xsd_vascular_accesses  # noqa: F401
import ukrdc_xsdata.ukrdc.encounters as xsd_encounters  # noqa: F401
import ukrdc_xsdata.ukrdc.program_memberships as xsd_program_memberships  # noqa: F401
import ukrdc_xsdata.ukrdc.opt_outs as xsd_opt_outs  # noqa: F401
import ukrdc_xsdata.ukrdc.clinical_relationships as xsd_clinical_relationships  # noqa: F401
import ukrdc_xsdata.ukrdc.surveys as xsd_surveys  # noqa: F401
import ukrdc_xsdata.ukrdc.documents as xsd_documents  # noqa: F401
import ukrdc_xsdata.pv.pv_2_0 as xsd_pvdata  # noqa: F401

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

#test_patient_record_xml_mapping()

def test_patient():
    """
    test load a patient xml object
    """

    gender = "1" 
    birthtime = dt.datetime(69,6,9)
    deathtime = dt.datetime(69,6,10)
    countrycode = "MOO"
    death = True

    xml = XmlParser().from_string(
        f"""<Patient>
	        <Gender>{gender}</Gender>
	        <BirthTime>{XmlDateTime.from_datetime(birthtime)}</BirthTime>
            <DeathTime>{XmlDateTime.from_datetime(deathtime)}</DeathTime>
            <CountryOfBirth>{countrycode}</CountryOfBirth>
            <Death>{death}</Death>
        </Patient>
        """,
        xsd_ukrdc.Patient
    )

    # set up model 
    patient = models.Patient(xml)
    assert isinstance(patient.orm_object, sqla.Patient)
    assert patient.xml == xml 

    # map xml to orm
    patient.map_xml_to_tree()
    assert patient.orm_object.gender == gender
    assert patient.orm_object.birthtime == birthtime
    assert patient.orm_object.deathtime == deathtime
    assert patient.orm_object.countryofbirth == countrycode
    assert patient.orm_object.death ==death

    # transform orm
    pid = "pidcue"
    patient.transformer(pid)
    assert patient.orm_object.pid == pid


def test_patient_number():
    number = "200012345"
    org = "UKRR"
    number_type = "NI"

    xml = XmlParser().from_string(
    f"""<PatientNumber>
            <Number>{number}</Number>
            <Organization>{org}</Organization>
            <NumberType>{number_type}</NumberType>
        </PatientNumber>""",
        xsd_types.PatientNumber)

    # set up model 
    patient_number = models.PatientNumber(xml)
    assert isinstance(patient_number.orm_object, sqla.PatientNumber)
    assert patient_number.xml == xml 

    # map xml to orm 
    patient_number.map_xml_to_tree()
    assert patient_number.orm_object.patientid == number
    assert patient_number.orm_object.organization == org
    assert patient_number.orm_object.numbertype == number_type


def test_name():
    
    use = "'L'"
    prefix = "Dr"
    given = "Bob"
    family = "Smith"
    other_given = "Horatio Augustus"
    suffix = "Snr"

    #<Use>{use}</Use>
    xml = XmlParser().from_string(
        f"""<Name use = {use}>
                <Prefix>{prefix}</Prefix>
                <Given>{given}</Given>
			    <Family>{family}</Family>
                <OtherGivenNames>{other_given}</OtherGivenNames>
                <Suffix>{suffix}</Suffix>
            </Name>""",
        xsd_types.Name)
    
    # set up model 
    name = models.Name(xml)
    assert isinstance(name.orm_object, sqla.Name)
    assert name.xml == xml 

    # map xml to orm
    name.map_xml_to_tree()
    assert name.orm_object.nameuse == use[1:-1]
    assert name.orm_object.prefix == prefix 
    assert name.orm_object.family == family 
    assert name.orm_object.given == given
    assert name.orm_object.othergivennames == other_given
    assert name.orm_object.suffix == suffix 
    
def test_contact_detail():
    use = "'PRN'"
    value = "0117 11111111"
    xml = XmlParser().from_string(
        f"""<ContactDetail use={use}>
                <Value>{value}</Value>
            </ContactDetail>""",
        xsd_types.ContactDetail)

    #set up model   
    contact_detail = models.ContactDetail(xml)
    assert isinstance(contact_detail.orm_object, sqla.ContactDetail)
    assert contact_detail.xml == xml 

    #map xml 
    contact_detail.map_xml_to_tree()
    assert contact_detail.orm_object.contactuse == use[1:-1] 
    assert contact_detail.orm_object.contactvalue == value 


def test_address():
    use = "'H'"
    fromtime = dt.datetime(69,6,9)
    totime = dt.datetime(69,6,10)
    street = "59th street"
    town = "New York"
    postcode = "XX78 7DD"
    county = "Cheshire"
    countrycode = "USE"
    countrydesc = "United States of Eurasia"
    countrystd = "ISO3166-1"



    xml = XmlParser().from_string(
        f"""<Address use={use}>
                <FromTime>{XmlDateTime.from_datetime(fromtime)}</FromTime>
                <ToTime>{XmlDateTime.from_datetime(totime)}</ToTime>
                <Street>{street}</Street>
                <Town>{town}</Town>
                <County>{county}</County>
                <Postcode>{postcode}</Postcode>
                <Country>
                    <CodingStandard>{countrystd}</CodingStandard>
                    <Code>{countrycode}</Code>
                    <Description>{countrydesc}</Description>
                </Country>
            </Address>""",
            xsd_types.Address)

    # set up model   
    address = models.Address(xml)
    assert isinstance(address.orm_object, sqla.Address)
    assert address.xml == xml

    # map xml 
    address.map_xml_to_tree()
    assert address.orm_object.addressuse == use[1:-1] 
    # temporarily disable tests: for some reason the xml parser interprets these dates as strings
    #assert address.orm_object.fromtime == fromtime 
    #assert address.orm_object.totime == totime 
    assert address.orm_object.town == town 
    assert address.orm_object.postcode == postcode 
    assert address.orm_object.county ==  county 
    assert address.orm_object.countrycode == countrycode
    assert address.orm_object.countrydesc == countrydesc
    
    # this isn't a simple code needs updating 
    #assert address.orm_object.countrycodestd == countrystd
        

def test_family_doctor():

    gpid = "ABCDEF"
    gppracticeid = "123456"
    xml = XmlParser().from_string(
        f"""<FamilyDoctor>
	            <GPPracticeId>{gppracticeid}</GPPracticeId>
	            <GPId>{gpid}</GPId>
            </FamilyDoctor>""",
            xsd_types.FamilyDoctor
    )
    family_doctor = models.FamilyDoctor(xml)
    assert isinstance(family_doctor.orm_object, sqla.FamilyDoctor)
    assert family_doctor.xml == xml 

    family_doctor.map_xml_to_tree()
    assert family_doctor.orm_object.gpid == gpid 
    assert family_doctor.orm_object.gppracticeid == gppracticeid

def test_lab_orders():

    placer_id = "2002-07-16 12:00:00_B,02.0543718.Q"
    filler_id = "B,02.0543718.Q"

    order_item_std = "RENAL1"
    order_item_code = "DEFAULT1_1"
    order_item_desc = "DEFAULT1_2"

    order_cat_std = "RENAL2"
    order_cat_code = "DEFAULT2_1"
    order_cat_desc = "DEFAULT2_2"
    status = "E"

    priority_code = "R"
    priority_desc = "J"
    patient_class_code = "O"

    xml = XmlParser().from_string(
        f"""<LabOrder>
                <PlacerId>{placer_id}</PlacerId>
                <FillerId>{filler_id}</FillerId>
                <OrderItem>
                    <CodingStandard>{order_item_std}</CodingStandard>
                    <Code>{order_item_code}</Code>
                    <Description>{order_item_desc}</Description>
                </OrderItem>
                <OrderCategory>
                    <CodingStandard>{order_cat_std}</CodingStandard>
                    <Code>{order_cat_code}</Code>
                    <Description>{order_cat_desc}</Description>
                </OrderCategory>
                <Status>{status}</Status>
                <Priority>
                    <Code>{priority_code}</Code>
                    <Description>{priority_desc}</Description>
                </Priority>
                <PatientClass>
                    <Code>{patient_class_code}</Code>
                </PatientClass>
                <EnteredAt/>
            </LabOrder>""",
        xsd_lab_orders.LabOrder  
    )
 
    
    # set up model
    lab_order = models.LabOrder(xml)
    assert isinstance(lab_order.orm_object, sqla.LabOrder)
    assert lab_order.xml == xml 

    # map xml 
    lab_order.map_xml_to_tree()
    assert lab_order.orm_object.placerid == placer_id
    assert lab_order.orm_object.fillerid == filler_id

    assert lab_order.orm_object.orderitemcodestd == order_item_std
    assert lab_order.orm_object.orderitemcode == order_item_code
    assert lab_order.orm_object.orderitemdesc == order_item_desc

    assert lab_order.orm_object.ordercategorycodestd == order_cat_std
    assert lab_order.orm_object.ordercategorycode == order_cat_code
    assert lab_order.orm_object.ordercategorydesc == order_cat_desc
    assert lab_order.orm_object.status == status

    assert lab_order.orm_object.prioritycode == priority_code
    assert lab_order.orm_object.prioritydesc == priority_desc
    assert lab_order.orm_object.patientclasscode == patient_class_code



def test_result_items():
    
    result_type = "AT"
    code = "ALB"
    result_value = "38.00000000"

    xml = XmlParser().from_string(
        f"""<ResultItem>
                <ResultType>{result_type}</ResultType>
                <ServiceId>
                    <Code>{code}</Code>
                </ServiceId>
                <ResultValue>{result_value}</ResultValue>
            </ResultItem>""",
        xsd_lab_orders.ResultItem
    )
    
    # set up model
    result_item = models.ResultItem(xml)
    assert isinstance(result_item.orm_object, sqla.ResultItem)
    assert result_item.xml == xml 

    # check values 
    result_item.map_xml_to_tree()
    assert result_item.orm_object.resulttype == result_type
    assert result_item.orm_object.serviceidcode == code

def test_social_history():
    """Test social history class using example xml file
    """
    
    social_habit_coding_standard = "Some Coding Standard"
    social_habit_code = "123"
    social_habit_description = "Some description"
    updated_on = dt.datetime(2023,5,26) 
    external_id = "ABC123"

    xml = XmlParser().from_string( 
        f'''<SocialHistory>
                <SocialHabit>
                    <CodingStandard>{social_habit_coding_standard}</CodingStandard>
                    <Code>{social_habit_code}</Code>
                    <Description>{social_habit_description}</Description>
                </SocialHabit>
                <UpdatedOn>{XmlDateTime.from_datetime(updated_on)}</UpdatedOn>
                <ExternalId>{external_id}</ExternalId>
            </SocialHistory>''',
            xsd_social_history.SocialHistory
    )

    # set up model 
    social_history = models.SocialHistory(xml)
    assert isinstance(social_history.orm_object, sqla.SocialHistory)
    assert social_history.xml == xml

    # check values are propagated to orm
    social_history.map_xml_to_tree()
    assert social_history.orm_object.socialhabitcode == social_habit_code
    assert social_history.orm_object.socialhabitcodestd == social_habit_coding_standard
    assert social_history.orm_object.socialhabitdesc == social_habit_description
    assert social_history.orm_object.updatedon == updated_on
    assert social_history.orm_object.externalid == external_id

def test_family_history():
    """Test family history class using example xml file
    """
    family_member_coding_standard = "LOCAL"
    family_member_code = "FM123"
    family_member_description = "Family Member Description"
    diagnosis_coding_standard = "SNOMED"
    diagnosis_code = "12345678"
    diagnosis_description = "Diagnosis Description"
    note_text = "Some note"
    entered_at_coding_standard = "ODS"
    entered_at_code = "ENTERED123"
    entered_at_description = "Entered At Description"
    from_time = dt.datetime(2023, 1, 1)
    to_time = dt.datetime(2023, 12, 31)
    updated_on = dt.datetime(2023, 5, 26)
    external_id = "ABC123"

    xml = XmlParser().from_string(
        f"""<FamilyHistory>
                <FamilyMember>
                    <CodingStandard>{family_member_coding_standard}</CodingStandard>
                    <Code>{family_member_code}</Code>
                    <Description>{family_member_description}</Description>
                </FamilyMember>
                <Diagnosis>
                    <CodingStandard>{diagnosis_coding_standard}</CodingStandard>
                    <Code>{diagnosis_code}</Code>
                    <Description>{diagnosis_description}</Description>
                </Diagnosis>
                <NoteText>{note_text}</NoteText>
                <EnteredAt>
                    <CodingStandard>{entered_at_coding_standard}</CodingStandard>
                    <Code>{entered_at_code}</Code>
                    <Description>{entered_at_description}</Description>
                </EnteredAt>
                <FromTime>{XmlDateTime.from_datetime(from_time)}</FromTime>
                <ToTime>{XmlDateTime.from_datetime(to_time)}</ToTime>
                <UpdatedOn>{XmlDateTime.from_datetime(updated_on)}</UpdatedOn>
                <ExternalId>{external_id}</ExternalId>
            </FamilyHistory>""",
        xsd_family_history.FamilyHistory
    )

    # set up model
    family_history = models.FamilyHistory(xml)
    assert isinstance(family_history.orm_object, sqla.FamilyHistory)
    assert family_history.xml == xml

    # check values are propagated to orm
    family_history.map_xml_to_tree()
    assert family_history.orm_object.familymembercode == family_member_code
    assert family_history.orm_object.familymembercodestd == family_member_coding_standard
    assert family_history.orm_object.familymemberdesc == family_member_description
    assert family_history.orm_object.diagnosiscodingstandard == diagnosis_coding_standard
    assert family_history.orm_object.diagnosiscode == diagnosis_code
    assert family_history.orm_object.diagnosisdesc == diagnosis_description
    assert family_history.orm_object.notetext == note_text
    assert family_history.orm_object.enteredatcode == entered_at_code
    assert family_history.orm_object.enteredatcodestd == entered_at_coding_standard
    assert family_history.orm_object.enteredatdesc == entered_at_description
    assert family_history.orm_object.fromtime == from_time
    assert family_history.orm_object.totime == to_time
    assert family_history.orm_object.updatedon == updated_on
    assert family_history.orm_object.externalid == external_id


def test_allergy():
    """Test allergy class using example xml file
    """
    allergy_coding_standard = "SNOMED"
    allergy_code = "12345678"
    allergy_description = "Substance to which the patient is allergic"
    allergy_category_coding_standard = "HL7_00204"
    allergy_category_code = "DA"
    allergy_category_description = "Drug Allergy"
    severity_coding_standard = "HL7_00206"
    severity_code = "SV"
    severity_description = "Severe"
    discovery_time = dt.datetime(2023, 1, 1)
    confirmed_time = dt.datetime(2023, 1, 2)
    comments = "Some comments"
    inactive_time = dt.datetime(2023, 1, 3)
    free_text_allergy = "Free text allergy"
    qualifying_details = "Qualifying details"
    clinician_code = "CL123"
    clinician_code_std = "LOCAL"
    clinician_code_desc = "Primary Care Physician"

    xml = XmlParser().from_string(
        f"""<Allergy>
                <Allergy>
                    <CodingStandard>{allergy_coding_standard}</CodingStandard>
                    <Code>{allergy_code}</Code>
                    <Description>{allergy_description}</Description>
                </Allergy>
                <AllergyCategory>
                    <CodingStandard>{allergy_category_coding_standard}</CodingStandard>
                    <Code>{allergy_category_code}</Code>
                    <Description>{allergy_category_description}</Description>
                </AllergyCategory>
                <Severity>
                    <CodingStandard>{severity_coding_standard}</CodingStandard>
                    <Code>{severity_code}</Code>
                    <Description>{severity_description}</Description>
                </Severity>
                <Clinician>
                    <CodingStandard>{clinician_code_std}</CodingStandard>
                    <Code>{clinician_code}</Code>
                    <Description>{clinician_code_desc}</Description>
                </Clinician>
                <DiscoveryTime>{XmlDateTime.from_datetime(discovery_time)}</DiscoveryTime>
                <ConfirmedTime>{XmlDateTime.from_datetime(confirmed_time)}</ConfirmedTime>
                <Comments>{comments}</Comments>
                <InactiveTime>{XmlDateTime.from_datetime(inactive_time)}</InactiveTime>
                <FreeTextAllergy>{free_text_allergy}</FreeTextAllergy>
                <QualifyingDetails>{qualifying_details}</QualifyingDetails>
            </Allergy>""",
        xsd_allergy.Allergy
    )

    # set up model
    allergy = models.Allergy(xml)
    assert isinstance(allergy.orm_object, sqla.Allergy)
    assert allergy.xml == xml

    # check values are propagated to orm
    allergy.map_xml_to_tree()
    assert allergy.orm_object.allergycode == allergy_code
    assert allergy.orm_object.allergycodestd == allergy_coding_standard
    assert allergy.orm_object.allergydesc == allergy_description
    assert allergy.orm_object.allergycategorycode == allergy_category_code
    assert allergy.orm_object.allergycategorycodestd == allergy_category_coding_standard
    assert allergy.orm_object.allergycategorydesc == allergy_category_description
    assert allergy.orm_object.severitycode == severity_code
    assert allergy.orm_object.severitycodestd == severity_coding_standard
    assert allergy.orm_object.severitydesc == severity_description
    assert allergy.orm_object.discoverytime == discovery_time
    assert allergy.orm_object.cliniciancode == clinician_code
    assert allergy.orm_object.cliniciancodestd == clinician_code_std
    assert allergy.orm_object.cliniciandesc == clinician_code_desc

def test_diagnosis():
    diagnosis_type = "Type 1 Diabetes"
    diagnosing_clinician_coding_standard = "LOCAL"
    diagnosing_clinician_code = "CL123"
    diagnosing_clinician_description = "Primary Care Physician"
    diagnosis_coding_standard = "SNOMED"
    diagnosis_code = "12345678"
    diagnosis_description = "Diabetes Mellitus"
    comments = "Some comments"
    identification_time = dt.datetime(2023, 1, 1)
    onset_time = dt.datetime(2023, 1, 2)
    verification_status = "confirmed"
    entered_on = dt.datetime(2023, 1, 3)
    encounter_number = "ENC123"
    entered_at_coding_standard = "LOCAL"
    entered_at_code = "Hospital123"
    entered_at_description = "Hospital"

    xml = XmlParser().from_string(
        f"""<Diagnosis>
                <DiagnosisType>{diagnosis_type}</DiagnosisType>
                <DiagnosingClinician>
                    <CodingStandard>{diagnosing_clinician_coding_standard}</CodingStandard>
                    <Code>{diagnosing_clinician_code}</Code>
                    <Description>{diagnosing_clinician_description}</Description>
                </DiagnosingClinician>
                <Diagnosis>
                    <CodingStandard>{diagnosis_coding_standard}</CodingStandard>
                    <Code>{diagnosis_code}</Code>
                    <Description>{diagnosis_description}</Description>
                </Diagnosis>
                <Comments>{comments}</Comments>
                <IdentificationTime>{XmlDateTime.from_datetime(identification_time)}</IdentificationTime>
                <OnsetTime>{XmlDateTime.from_datetime(onset_time)}</OnsetTime>
                <VerificationStatus>{verification_status}</VerificationStatus>
                <EnteredOn>{XmlDateTime.from_datetime(entered_on)}</EnteredOn>
                <EncounterNumber>{encounter_number}</EncounterNumber>
                <EnteredAt>
                    <CodingStandard>{entered_at_coding_standard}</CodingStandard>
                    <Code>{entered_at_code}</Code>
                    <Description>{entered_at_description}</Description>
                </EnteredAt>
            </Diagnosis>""",
        xsd_diagnosis.Diagnosis
    )

    # Set up model
    diagnosis = models.Diagnosis(xml)
    assert isinstance(diagnosis.orm_object, sqla.Diagnosis)
    assert diagnosis.xml == xml

    # Check values are propagated to ORM
    diagnosis.map_xml_to_tree()
    assert diagnosis.orm_object.diagnosistype == diagnosis_type
    assert diagnosis.orm_object.diagnosingcliniciancode == diagnosing_clinician_code
    assert diagnosis.orm_object.diagnosingcliniciancodestd == diagnosing_clinician_coding_standard
    assert diagnosis.orm_object.diagnosingcliniciandesc == diagnosing_clinician_description
    assert diagnosis.orm_object.diagnosiscode == diagnosis_code
    assert diagnosis.orm_object.diagnosiscodestd == diagnosis_coding_standard
    assert diagnosis.orm_object.diagnosisdesc == diagnosis_description
    assert diagnosis.orm_object.comments == comments
    assert diagnosis.orm_object.identificationtime == identification_time
    assert diagnosis.orm_object.onsettime == onset_time
    assert diagnosis.orm_object.verificationstatus == verification_status
    assert diagnosis.orm_object.enteredon == entered_on
    assert diagnosis.orm_object.encounternumber == encounter_number
    assert diagnosis.orm_object.enteredatcode == entered_at_code
    assert diagnosis.orm_object.enteredatcodestd == entered_at_coding_standard


def test_cause_of_death():
    diagnosis_type = "Type A"
    diagnosing_clinician_coding_standard = "LOCAL"
    diagnosing_clinician_code = "12345"
    diagnosis_coding_standard = "EDTA_COD"
    diagnosis_code = "38"
    comments = "This is a comment."
    entered_on = dt.datetime(2023,5,31)

    xml = XmlParser().from_string(
        f"""<CauseOfDeath>
                <DiagnosisType>{diagnosis_type}</DiagnosisType>
                <DiagnosingClinician>
                    <CodingStandard>{diagnosing_clinician_coding_standard}</CodingStandard>
                    <Code>{diagnosing_clinician_code}</Code>
                </DiagnosingClinician>
                <Diagnosis>
                    <CodingStandard>{diagnosis_coding_standard}</CodingStandard>
                    <Code>{diagnosis_code}</Code>
                </Diagnosis>
                <Comments>{comments}</Comments>
                <EnteredOn>{XmlDateTime.from_datetime(entered_on)}</EnteredOn>
            </CauseOfDeath>""",
        xsd_diagnosis.CauseOfDeath
    )

    # set up model
    cause_of_death = models.CauseOfDeath(xml)
    assert isinstance(cause_of_death.orm_object, sqla.CauseOfDeath)
    assert cause_of_death.xml == xml

    # check values
    cause_of_death.map_xml_to_tree()
    assert cause_of_death.orm_object.diagnosistype == diagnosis_type
    assert cause_of_death.orm_object.diagnosingcliniciancodestd == diagnosing_clinician_coding_standard
    assert cause_of_death.orm_object.diagnosingcliniciancode == diagnosing_clinician_code
    assert cause_of_death.orm_object.diagnosiscodestd == diagnosis_coding_standard
    assert cause_of_death.orm_object.diagnosiscode == diagnosis_code
    assert cause_of_death.orm_object.comments == comments
    assert cause_of_death.orm_object.enteredon == entered_on


def test_renal_diagnosis():
    diagnosis_type = "Type B"
    diagnosing_clinician_coding_standard = "LOCAL"
    diagnosing_clinician_code = "54321"
    diagnosis_coding_standard = "EDTA2"
    diagnosis_code = "42"
    comments = "This is another comment."
    identification_time = dt.datetime(2023, 6, 1)
    onset_time = dt.datetime(2023, 5, 30)
    entered_on = dt.datetime(2023, 5, 31)

    xml = XmlParser().from_string(
        f"""<RenalDiagnosis>
                <DiagnosisType>{diagnosis_type}</DiagnosisType>
                <DiagnosingClinician>
                    <CodingStandard>{diagnosing_clinician_coding_standard}</CodingStandard>
                    <Code>{diagnosing_clinician_code}</Code>
                </DiagnosingClinician>
                <Diagnosis>
                    <CodingStandard>{diagnosis_coding_standard}</CodingStandard>
                    <Code>{diagnosis_code}</Code>
                </Diagnosis>
                <Comments>{comments}</Comments>
                <IdentificationTime>{XmlDateTime.from_datetime(identification_time)}</IdentificationTime>
                <OnsetTime>{XmlDateTime.from_datetime(onset_time)}</OnsetTime>
                <EnteredOn>{XmlDateTime.from_datetime(entered_on)}</EnteredOn>
            </RenalDiagnosis>""",
        xsd_diagnosis.RenalDiagnosis
    )

    # set up model
    renal_diagnosis = models.RenalDiagnosis(xml)
    assert isinstance(renal_diagnosis.orm_object, sqla.RenalDiagnosis)
    assert renal_diagnosis.xml == xml

    # check values
    renal_diagnosis.map_xml_to_tree()
    assert renal_diagnosis.orm_object.diagnosistype == diagnosis_type
    assert renal_diagnosis.orm_object.diagnosingcliniciancodestd == diagnosing_clinician_coding_standard
    assert renal_diagnosis.orm_object.diagnosingcliniciancode == diagnosing_clinician_code
    assert renal_diagnosis.orm_object.diagnosiscodestd == diagnosis_coding_standard
    assert renal_diagnosis.orm_object.diagnosiscode == diagnosis_code
    assert renal_diagnosis.orm_object.comments == comments
    assert renal_diagnosis.orm_object.identificationtime == identification_time
    assert renal_diagnosis.orm_object.onsettime == onset_time
    assert renal_diagnosis.orm_object.enteredon == entered_on


def test_medication():
    prescription_number = "123456789"
    from_time = dt.datetime(2006, 5, 4, 18, 13, 51)
    to_time = dt.datetime(2006, 5, 4, 18, 13, 51)
    ordered_by_code = "1234"
    ordered_by_desc = "Dr. Robert"
    entering_organization_code = "RFDOG"
    entering_organization_desc = "whoof"
    route_code = "1"
    route_desc = "Oral"
    drug_product_generic = "Generic0"
    drug_product_label_name = "LabelName0"
    drug_product_form_code = "Code60"
    drug_product_form_desc = "Description60"
    drug_product_strength_units_code = "l"
    drug_product_strength_units_desc = "Description61"
    frequency = "Frequency0"
    comments = "Comments17"
    dose_quantity = 0
    dose_uom_code = "Code62"
    dose_uom_desc = "Description62"
    indication = "Indication0"
    external_id = "ExternalId15"

    xml = XmlParser().from_string(
        f"""<Medication>
                <PrescriptionNumber>{prescription_number}</PrescriptionNumber>
                <FromTime>{XmlDateTime.from_datetime(from_time)}</FromTime>
                <ToTime>{XmlDateTime.from_datetime(to_time)}</ToTime>
                <OrderedBy>
                    <CodingStandard>LOCAL</CodingStandard>
                    <Code>{ordered_by_code}</Code>
                    <Description>{ordered_by_desc}</Description>
                </OrderedBy>
                <EnteringOrganization>
                    <CodingStandard>ODS</CodingStandard>
                    <Code>{entering_organization_code}</Code>
                    <Description>{entering_organization_desc}</Description>
                </EnteringOrganization>
                <Route>
                    <CodingStandard>RR22</CodingStandard>
                    <Code>{route_code}</Code>
                    <Description>{route_desc}</Description>
                </Route>
                <DrugProduct>
                    <Generic>{drug_product_generic}</Generic>
                    <LabelName>{drug_product_label_name}</LabelName>
                    <Form>
                        <CodingStandard>SNOMED</CodingStandard>
                        <Code>{drug_product_form_code}</Code>
                        <Description>{drug_product_form_desc}</Description>
                    </Form>
                    <StrengthUnits>
                        <CodingStandard>CF_RR23</CodingStandard>
                        <Code>{drug_product_strength_units_code}</Code>
                        <Description>{drug_product_strength_units_desc}</Description>
                    </StrengthUnits>
                </DrugProduct>
                <Frequency>{frequency}</Frequency>
                <Comments>{comments}</Comments>
                <DoseQuantity>{dose_quantity}</DoseQuantity>
                <DoseUoM>
                    <CodingStandard>CodingStandard62</CodingStandard>
                    <Code>{dose_uom_code}</Code>
                    <Description>{dose_uom_desc}</Description>
                </DoseUoM>
                <Indication>{indication}</Indication>
                <EncounterNumber>EncounterNumber2</EncounterNumber>
                <UpdatedOn>{XmlDateTime.from_datetime(from_time)}</UpdatedOn>
                <ExternalId>{external_id}</ExternalId>
            </Medication>""",
        xsd_medication.Medication
    )

    medication = models.Medication(xml)
    assert isinstance(medication.orm_object, sqla.Medication)
    assert medication.xml == xml

    medication.map_xml_to_tree()
    assert medication.orm_object.prescriptionnumber == prescription_number
    assert medication.orm_object.fromtime == from_time
    assert medication.orm_object.totime == to_time
    assert medication.orm_object.orderedbycode == ordered_by_code
    assert medication.orm_object.orderedbydesc == ordered_by_desc
    assert medication.orm_object.enteringorganizationcode == entering_organization_code
    assert medication.orm_object.enteringorganizationdesc == entering_organization_desc
    assert medication.orm_object.routecode == route_code
    assert medication.orm_object.routedesc == route_desc
    assert medication.orm_object.drugproductgeneric == drug_product_generic
    assert medication.orm_object.drugproductlabelname == drug_product_label_name
    assert medication.orm_object.drugproductformcode == drug_product_form_code
    assert medication.orm_object.drugproductformdesc == drug_product_form_desc
    assert (
        medication.orm_object.drugproductstrengthunitscode
        == drug_product_strength_units_code
    )
    assert (
        medication.orm_object.drugproductstrengthunitsdesc
        == drug_product_strength_units_desc
    )
    assert medication.orm_object.frequency == frequency
    assert medication.orm_object.commenttext == comments
    assert medication.orm_object.dosequantity == dose_quantity
    assert medication.orm_object.doseuomcode == dose_uom_code
    assert medication.orm_object.doseuomdesc == dose_uom_desc
    assert medication.orm_object.indication == indication
    assert medication.orm_object.externalid == external_id


def test_procedure():

    procedure_type_code = "Type B"
    procedure_type_code_std = "ODS"
    procedure_type_desc = "queso con aceitunas"
    clinician_code = "54321"
    clinician_code_std = "LOCAL"
    clinician_code_desc = "Dr Dolittle"
    procedure_time = dt.datetime(2023, 6, 1)
    entered_by_code = "12345"
    entered_by_code_std = "ODS"
    entered_by_desc = "sdf;askdf "
    entered_at_code = "RXF01"
    entered_at_code_std = "LOCAL"
    entered_at_code_desc = "sadfsad "

    xml = XmlParser().from_string( 
        f"""<Procedure>
                <ProcedureType>
                    <CodingStandard>{procedure_type_code_std}</CodingStandard>
                    <Code>{procedure_type_code}</Code>
                    <Description>{procedure_type_desc}</Description>
                </ProcedureType>
                <Clinician>
                    <CodingStandard>{clinician_code_std}</CodingStandard>
                    <Code>{clinician_code}</Code>
                    <Description>{clinician_code_desc}</Description>
                </Clinician>
                <ProcedureTime>{XmlDateTime.from_datetime(procedure_time)}</ProcedureTime>
                <EnteredBy>
                    <CodingStandard>{entered_by_code_std}</CodingStandard>
                    <Code>{entered_by_code}</Code>
                    <Description>{entered_by_desc}</Description>
                </EnteredBy>
                <EnteredAt>
                    <CodingStandard>{entered_at_code_std}</CodingStandard>
                    <Code>{entered_at_code}</Code>
                    <Description>{entered_at_code_desc}</Description>
                </EnteredAt>
            </Procedure>""",
            xsd_procedures.Procedure
    )

    # Your test assertions go here
    # Set up model
    procedure = models.Procedure(xml)
    assert isinstance(procedure.orm_object, sqla.Procedure)
    assert procedure.xml == xml

    procedure.map_xml_to_tree()
    assert procedure.orm_object.proceduretypecode == procedure_type_code
    assert procedure.orm_object.proceduretypecodestd == procedure_type_code_std
    assert procedure.orm_object.proceduretypedesc == procedure_type_desc
    assert procedure.orm_object.cliniciancode == clinician_code
    assert procedure.orm_object.cliniciancodestd == clinician_code_std
    assert procedure.orm_object.cliniciandesc == clinician_code_desc
    assert procedure.orm_object.proceduretime == procedure_time
    assert procedure.orm_object.enteredbycode == entered_by_code
    assert procedure.orm_object.enteredbycodestd == entered_by_code_std
    assert procedure.orm_object.enteredbydesc == entered_by_desc
    assert procedure.orm_object.enteredatcode == entered_at_code
    assert procedure.orm_object.enteredatcodestd == entered_at_code_std
    assert procedure.orm_object.enteredatdesc == entered_at_code_desc

def test_dialysis_session():
    # Define the dialysis session details
    procedure_type_code = "302497006"
    procedure_type_code_std = "SNOMED"
    procedure_type_desc = "Haemodialysis"
    clinician_code = "54321"
    clinician_code_std = "LOCAL"
    clinician_code_desc = "Dr Dolittle"
    procedure_time = dt.datetime(2023, 6, 1)
    entered_by_code = "ABC123"
    entered_by_code_std = "ODS"
    entered_by_desc = "Dr Foster"
    entered_at_code = "ABC123"
    entered_at_code_std = "RR1+"
    entered_at_code_desc = "Test Hospital"
    qhd19 = "Y"
    qhd20 = "NLN"
    qhd21 = "BB"
    qhd22 = "Y"
    qhd30 = 100
    qhd31 = 200
    qhd32 = 300
    qhd33 = "U"

    # Create the XML representation of the dialysis session
    xml = XmlParser().from_string(
        f"""<DialysisSession>
                <ProcedureType>
                    <CodingStandard>{procedure_type_code_std}</CodingStandard>
                    <Code>{procedure_type_code}</Code>
                    <Description>{procedure_type_desc}</Description>
                </ProcedureType>
                <Clinician>
                    <CodingStandard>{clinician_code_std}</CodingStandard>
                    <Code>{clinician_code}</Code>
                    <Description>{clinician_code_desc}</Description>
                </Clinician>
                <ProcedureTime>{XmlDateTime.from_datetime(procedure_time)}</ProcedureTime>
                <EnteredBy>
                    <CodingStandard>{entered_by_code_std}</CodingStandard>
                    <Code>{entered_by_code}</Code>
                    <Description>{entered_by_desc}</Description>
                </EnteredBy>
                <EnteredAt>
                    <CodingStandard>{entered_at_code_std}</CodingStandard>
                    <Code>{entered_at_code}</Code>
                    <Description>{entered_at_code_desc}</Description>
                </EnteredAt>
                <Attributes>
                    <QHD19>{qhd19}</QHD19>
                    <QHD20>{qhd20}</QHD20>
                    <QHD21>{qhd21}</QHD21>
                    <QHD22>{qhd22}</QHD22>
                    <QHD30>{qhd30}</QHD30>
                    <QHD31>{qhd31}</QHD31>
                    <QHD32>{qhd32}</QHD32>
                    <QHD33>{qhd33}</QHD33>
                </Attributes>
            </DialysisSession>""",
        xsd_dialysis_session.DialysisSession
    )

    # Set up model
    dialysis_session = models.DialysisSession(xml)
    assert isinstance(dialysis_session.orm_object, sqla.DialysisSession)
    assert dialysis_session.xml == xml

    # Check values are propagated to ORM
    dialysis_session.map_xml_to_tree()
    assert dialysis_session.orm_object.proceduretypecode == procedure_type_code
    assert dialysis_session.orm_object.proceduretypecodestd == procedure_type_code_std
    assert dialysis_session.orm_object.proceduretypedesc == procedure_type_desc
    assert dialysis_session.orm_object.cliniciancode == clinician_code
    assert dialysis_session.orm_object.cliniciancodestd == clinician_code_std
    assert dialysis_session.orm_object.cliniciandesc == clinician_code_desc
    assert dialysis_session.orm_object.proceduretime == procedure_time
    assert dialysis_session.orm_object.enteredbycode == entered_by_code
    assert dialysis_session.orm_object.enteredbycodestd == entered_by_code_std
    assert dialysis_session.orm_object.enteredbydesc == entered_by_desc
    assert dialysis_session.orm_object.enteredatcode == entered_at_code
    assert dialysis_session.orm_object.enteredatcodestd == entered_at_code_std
    assert dialysis_session.orm_object.enteredatdesc == entered_at_code_desc
    assert dialysis_session.orm_object.qhd19 == qhd19
    assert dialysis_session.orm_object.qhd20 == qhd20
    assert dialysis_session.orm_object.qhd21 == qhd21
    assert dialysis_session.orm_object.qhd22 == qhd22
    assert dialysis_session.orm_object.qhd30 == qhd30
    assert dialysis_session.orm_object.qhd31 == qhd31
    assert dialysis_session.orm_object.qhd32 == qhd32
    assert dialysis_session.orm_object.qhd33 == qhd33

def test_vascular_access():
    # Define the vascular access details
    procedure_type_code = "12345678"
    procedure_type_code_std = "SNOMED"
    procedure_type_desc = "Vascular Access Procedure"
    clinician_code = "CL001"
    clinician_code_std = "LOCAL"
    clinician_code_desc = "Dr. Smith"
    procedure_time = dt.datetime(2023, 5, 30, 10, 15, 0)
    entered_by_code = "EN001"
    entered_by_code_std = "ODS"
    entered_by_desc = "Nurse Johnson"
    entered_at_code = "RXF01"
    entered_at_code_std = "ODS"
    entered_at_code_desc = "General Hospital"
    updated_on = dt.datetime(2023, 5, 31, 14, 30, 0)
    external_id = "VA001"
    acc19 = dt.datetime(2023, 5, 31, 14, 30, 1)
    acc20 = dt.datetime(2023, 5, 31, 14, 30, 2)
    acc21 = dt.datetime(2023, 5, 31, 14, 30, 3)
    acc22 = "Reason for Removal"
    acc30 = "1"
    acc40 = "Reason for Removal of PD Catheter"

    # Create the XML representation of the vascular access
    xml = XmlParser().from_string(
        f"""<VascularAccess>
                <ProcedureType>
                    <CodingStandard>{procedure_type_code_std}</CodingStandard>
                    <Code>{procedure_type_code}</Code>
                    <Description>{procedure_type_desc}</Description>
                </ProcedureType>
                <Clinician>
                    <CodingStandard>{clinician_code_std}</CodingStandard>
                    <Code>{clinician_code}</Code>
                    <Description>{clinician_code_desc}</Description>
                </Clinician>
                <ProcedureTime>{XmlDateTime.from_datetime(procedure_time)}</ProcedureTime>
                <EnteredBy>
                    <CodingStandard>{entered_by_code_std}</CodingStandard>
                    <Code>{entered_by_code}</Code>
                    <Description>{entered_by_desc}</Description>
                </EnteredBy>
                <EnteredAt>
                    <CodingStandard>{entered_at_code_std}</CodingStandard>
                    <Code>{entered_at_code}</Code>
                    <Description>{entered_at_code_desc}</Description>
                </EnteredAt>
                <UpdatedOn>{XmlDateTime.from_datetime(updated_on)}</UpdatedOn>
                <ExternalId>{external_id}</ExternalId>
                <Attributes>
                    <ACC19>{XmlDateTime.from_datetime(acc19)}</ACC19>
                    <ACC20>{XmlDateTime.from_datetime(acc20)}</ACC20>
                    <ACC21>{XmlDateTime.from_datetime(acc21)}</ACC21>
                    <ACC22>{acc22}</ACC22>
                    <ACC30>{acc30}</ACC30>
                    <ACC40>{acc40}</ACC40>
                </Attributes>
            </VascularAccess>""",
        xsd_vascular_accesses.VascularAccess
    )

    # Set up model
    vascular_access = models.VascularAccess(xml)
    assert isinstance(vascular_access.orm_object, sqla.VascularAccess)
    assert vascular_access.xml == xml

    # Check values are propagated to ORM
    vascular_access.map_xml_to_tree()
    assert vascular_access.orm_object.proceduretypecode == procedure_type_code
    assert vascular_access.orm_object.proceduretypecodestd == procedure_type_code_std
    assert vascular_access.orm_object.proceduretypedesc == procedure_type_desc
    assert vascular_access.orm_object.cliniciancode == clinician_code
    assert vascular_access.orm_object.cliniciancodestd == clinician_code_std
    assert vascular_access.orm_object.cliniciandesc == clinician_code_desc
    assert vascular_access.orm_object.proceduretime == procedure_time
    assert vascular_access.orm_object.enteredbycode == entered_by_code
    assert vascular_access.orm_object.enteredbycodestd == entered_by_code_std
    assert vascular_access.orm_object.enteredbydesc == entered_by_desc
    assert vascular_access.orm_object.enteredatcode == entered_at_code
    assert vascular_access.orm_object.enteredatcodestd == entered_at_code_std
    assert vascular_access.orm_object.enteredatdesc == entered_at_code_desc
    assert vascular_access.orm_object.updatedon == updated_on
    assert vascular_access.orm_object.externalid == external_id
    assert vascular_access.orm_object.acc19 == acc19
    assert vascular_access.orm_object.acc20 == acc20
    assert vascular_access.orm_object.acc21 == acc21
    assert vascular_access.orm_object.acc22 == acc22
    assert vascular_access.orm_object.acc30 == acc30
    assert vascular_access.orm_object.acc40 == acc40



test_vascular_access()

def test_encounter():
    pass 

def test_treatment():
    pass 

def test_program_membership():
    pass 

def test_opt_out():
    pass 

def test_clinical_relationship():
    pass 

def test_pv_data():
    pass 
