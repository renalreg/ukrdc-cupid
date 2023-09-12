from lxml import etree 
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string

def test_transplant_validation():
    # As the source of big headaches elsewhere putting some tests here
    v4_00_transplant_xml =  """<ukrdc:PatientRecord xmlns:ukrdc="http://www.rixg.org.uk/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <SendingFacility channelName="UKRDCSampleExtract" schemaVersion="4.0.0" time="2022-07-21T09:00:00">ABC123</SendingFacility>
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
                <Name use="L">
                    <Prefix>Mr</Prefix>
                    <Family>Surname</Family>
                    <Given>Forename</Given>
                </Name>
            </Names>
            <BirthTime>2006-05-04T18:13:51.0</BirthTime>
            <Gender>1</Gender>
        </Patient>
        <Procedures>
            <Transplant>
                <ProcedureType>
                    <CodingStandard>SNOMED</CodingStandard>
                    <Code>19647005</Code>
                    <Description>PEX</Description>
                </ProcedureType>
                <ProcedureTime>2006-05-04T18:13:51.0</ProcedureTime>
                <EnteredBy>
                    <CodingStandard>ODS</CodingStandard>
                    <Code>ABC123</Code>
                    <Description>Dr Foster</Description>
                </EnteredBy>
                <EnteredAt>
                    <CodingStandard>RR1+</CodingStandard>
                    <Code>ABC123</Code>
                    <Description>Test Hospital</Description>
                </EnteredAt>
                <UpdatedOn>2006-05-04T18:13:51.0</UpdatedOn>
                <ExternalId>1222333444</ExternalId>
                <DateRegistered>2006-01-04</DateRegistered>
                <DonorType>DBD</DonorType>
                <FailureDate>2006-05-04</FailureDate>
                <ColdIschaemicTime>90</ColdIschaemicTime>
                <HLAMismatchA>0</HLAMismatchA>
                <HLAMismatchB>1</HLAMismatchB>
                <HLAMismatchC>2</HLAMismatchC>
            </Transplant>
        </Procedures>
    </ukrdc:PatientRecord>"""

    errors = validate_rda_xml_string(v4_00_transplant_xml,schema_version="4.0.0")
    print(errors)
    assert not errors
#test_transplant_validation()