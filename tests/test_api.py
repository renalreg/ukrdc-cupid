def test_validation_errors(client):
    content = """
    <ukrdc:PatientRecord xmlns:ukrdc="http://www.rixg.org.uk/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <SendingFacility channelName="UKRDCSampleExtract" schemaVersion="4.0.0" time="2023-08-16T08:32:40.306453">ABC123</SendingFacility>
        <SendingExtract>UKRDC</SendingExtract>
        <Patient>
            <PatientNumbers>
                <PatientNumber>
                    <Number>66666</Number>
                    <Organization>LOCALHOSP</Organization>
                    <NumberType>MRN</NumberType>
                </PatientNumber>
                <PatientNumber>
                    <Number>1111111111</Number>
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
            <BirthTime>2006-05-04T18:13:51.0</BirthTime>
        </Patient>
        <Encounters>
            <Treatment>
                <AdmitReason>
                    <CodingStandard>CF_RR7_TREATMENT</CodingStandard>
                    <Code>903</Code>
                    <Description>Haemodialysis</Description>
                </AdmitReason>
            </Treatment>
        </Encounters>
    </ukrdc:PatientRecord>
    """

    response = client.post(
        "/parse/xml_validate/4.1.0", content=content, headers={"Content-Type": "application/xml"}
    )

    assert response.text == "XML file not valid against 4.1.0 schema.\nError on line 5. Element 'Patient': Missing child element(s). Expected is one of ( DeathTime, Gender ).\nError on line 29. Element 'AdmitReason': This element is not expected. Expected is one of ( EncounterNumber, FromTime ).\n"

def test_xml_load(client):
    content = """
    <ukrdc:PatientRecord xmlns:ukrdc="http://www.rixg.org.uk/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <SendingFacility channelName="UKRDCSampleExtract" time="2022-07-21T09:00:00" schemaVersion="4.2.0" >RFCAT</SendingFacility>
        <SendingExtract>UKRDC</SendingExtract>
        <Patient>
            <PatientNumbers>
                <PatientNumber>
                    <Number>AAA111B</Number>
                    <Organization>LOCALHOSP</Organization>
                    <NumberType>MRN</NumberType>
                </PatientNumber>
                <PatientNumber>
                    <Number>1111111111</Number>
                    <Organization>NHS</Organization>
                    <NumberType>NI</NumberType>
                </PatientNumber>
            </PatientNumbers>
            <Names>
                <Name use="L"/>
            </Names>
            <BirthTime>1969-06-09T00:00:00</BirthTime>
            <Gender>1</Gender>
        </Patient>
    </ukrdc:PatientRecord>"""

    response = client.post(
        "/store/upload_patient/overwrite", content=content, headers={"Content-Type": "application/xml"}
    )
    
    assert response.status_code == 200