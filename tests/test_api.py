from ukrdc_cupid.core.investigate.create_investigation import Investigation
from ukrdc_sqla.ukrdc import PatientRecord, Patient, PatientNumber
from sqlalchemy import select
import datetime as  dt

SCHEMA_VERSION = "4.2.0"

def xml_template(
        version:str, 
        elements:str,
        mrn:str = "66666",
        nhs:str = "1111111111",
        birthtime = "1912-04-14T23:40:00.0"
    ):
    content = f"""
    <ukrdc:PatientRecord xmlns:ukrdc="http://www.rixg.org.uk/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <SendingFacility channelName="UKRDCSampleExtract" schemaVersion="{version}" time="2023-08-16T08:32:40.306453">ABC123</SendingFacility>
        <SendingExtract>UKRDC</SendingExtract>
        <Patient>
            <PatientNumbers>
                <PatientNumber>
                    <Number>{mrn}</Number>
                    <Organization>LOCALHOSP</Organization>
                    <NumberType>MRN</NumberType>
                </PatientNumber>
                <PatientNumber>
                    <Number>{nhs}</Number>
                    <Organization>NHS</Organization>
                    <NumberType>NI</NumberType>
                </PatientNumber>
            </PatientNumbers>
            <Names>
                <Name use="L">
                    <Prefix>Mr</Prefix>
                    <Family>Sample</Family>
                    <Given>John</Given>
                </Name>
            </Names>
            <BirthTime>{birthtime}</BirthTime>
            <DeathTime>2023-06-18T09:45:00.0</DeathTime>
            <Gender>2</Gender>
        </Patient>
        {elements}
    </ukrdc:PatientRecord>"""
    return content

def test_xml_load(client):
    content = xml_template(SCHEMA_VERSION, "")

    response = client.post(
        "/store/upload_patient_file/overwrite", content=content, headers={"Content-Type": "application/xml"}
    )
    
    assert response.status_code == 200

def test_validation_errors(client):
    xml = """
        <Documents>
            paper panama
        </Documents>
        <LabOrders>
            Whoof Whoof
        </LabOrders>
        <MyAlienElement>
            <Extra>
                <Terrestial>sup</Terrestial>
            </Extra> 
        </MyAlienElement>
    """
    content = xml_template(SCHEMA_VERSION, xml)

    response = client.post(
        f"/parse/xml_validate/{SCHEMA_VERSION}", content=content, headers={"Content-Type": "application/xml"}
    )
    print(response.text)

    assert response.text == f"XML file not valid against {SCHEMA_VERSION} schema.\nError on line 30. Element 'Documents': Character content other than whitespace is not allowed because the content type is 'element-only'.\nError on line 33. Element 'LabOrders': This element is not expected. Expected is one of ( Encounters, ProgramMemberships, OptOuts, ClinicalRelationships, Surveys, Assessments, PVData ).\n"



def test_force_upload_file(client, ukrdc_test_session):
    # test_basic functionality of force merging
    
    # create fictitious patient
    pid_test = "1111111"
    ukrdcid = "\(00)/"
    nhs_num = "2222222222"
    birthtime = dt.datetime(1912,4,14,23,40)

    creation_date = dt.datetime.today()
    ukrdc_test_session.add(
        PatientRecord(
            sendingfacility = 'RFDOG',
            sendingextract = 'TESTY',
            repositorycreationdate=creation_date,
            repositoryupdatedate=creation_date,
            localpatientid = "4",
            pid = pid_test,
            ukrdcid = ukrdcid
        )
    )
    ukrdc_test_session.add(
        Patient(
            pid = pid_test,
            birthtime = birthtime
        )
    )


    ukrdc_test_session.add(
        PatientNumber(
            id = "3",
            pid = pid_test,
            patientid = nhs_num,
            organization = "NHS"
        )
    )
    ukrdc_test_session.add(
        PatientNumber(
            id = "4",
            pid = pid_test,
            patientid = "66666",
            organization = "MRN"
        )
    )
    ukrdc_test_session.commit()

    # Generate a file with different details 
    # the conflict in the patient id in this would cause something like a 
    # type 4 error (inconsistent MRN and NHS number) we simulate the process
    # of overwriting the patient with an xml file we know to be correct
    xml_overwrite = xml_template(SCHEMA_VERSION, "")
    investigation = Investigation(ukrdc_test_session, [(pid_test, ukrdcid)], 4)
    investigation.append_extras(xml = xml_overwrite)
    issue_id = investigation.issue.id
    #ukrdc_test_session = 

    response = client.post(
        f"/modify/force_merge_file/{issue_id}/{pid_test}"
    )

    print(response.content)
    
    assert response
    assert response.status_code == 200

    pat_num = ukrdc_test_session.execute(
        select(PatientNumber.patientid).where(PatientNumber.organization == "NHS")
    ).scalars().first()
    
    assert pat_num != nhs_num
    assert pat_num == "1111111111"

def test_delete_patient(client, ukrdc_test_session):
    pid = "test_delete"
    creation_date = dt.datetime.today()
    ukrdc_test_session.add(
        PatientRecord(
            sendingfacility = 'RFDOG',
            sendingextract = 'TESTY',
            repositorycreationdate=creation_date,
            repositoryupdatedate=creation_date,
            localpatientid = "4",
            pid = pid,
            ukrdcid = "test_id"
        )
    )
    ukrdc_test_session.commit()

    response = client.post(f"/modify/delete_patient/{pid}")

    assert response.status_code == 200

def test_non_ascii(client):
    my_lab_non_ascii = """
    <Medications>
        <Medication>
        <PrescriptionNumber>xxxxx</PrescriptionNumber>
        <FromTime>2020-07-03T00:00:00</FromTime>
        <ToTime>2020-07-08T17:28:13</ToTime>
        <Route>
            <CodingStandard>RR22</CodingStandard>
            <Code>9</Code>
            <Description>IV</Description>
        </Route>
        <DrugProduct>
            <Generic>ARANESP PREFILLED</Generic>
            <LabelName />
            <StrengthUnits>
            <CodingStandard>CF_RR23</CodingStandard>
            <Code>μg</Code>
            <Description>micrograms</Description>
            </StrengthUnits>
        </DrugProduct>
        <Frequency>q Friday</Frequency>
        <Comments />
        <DoseQuantity>30.0</DoseQuantity>
        <DoseUoM>
            <CodingStandard>CF_RR23</CodingStandard>
            <Code>μg</Code>
            <Description>micrograms</Description>
        </DoseUoM>
        </Medication>
    </Medications>
    """

    xml = xml_template(SCHEMA_VERSION, my_lab_non_ascii)
    response = client.post(
        "/store/upload_patient_file/overwrite", content=xml, headers={"Content-Type": "application/xml"}
    )

    assert response.status_code == 200

def test_empty_lab(client):
    xml = xml_template(SCHEMA_VERSION, "<LabOrders/>")
    response = client.post(
        "/store/upload_patient_file/overwrite", 
        content=xml, 
        headers={"Content-Type": "application/xml"}
    )

    assert response.status_code == 200

def test_no_start_stop():
    """This should check that the default 
    """
    assert True