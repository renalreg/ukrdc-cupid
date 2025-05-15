import glob
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string
from ukrdc_cupid.core.parse.xml_validate import SUPPORTED_VERSIONS


def test_transplant_validation():
    # As the source of big headaches elsewhere putting some tests here
    v4_00_transplant_xml = """<ukrdc:PatientRecord xmlns:ukrdc="http://www.rixg.org.uk/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
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
                <DonorType>DBD</DonorType>
                <DateRegistered>2006-01-04</DateRegistered>
                <FailureDate>2006-05-04</FailureDate>
                <ColdIschaemicTime>90</ColdIschaemicTime>
                <HLAMismatchA>0</HLAMismatchA>
                <HLAMismatchB>1</HLAMismatchB>
                <HLAMismatchC>2</HLAMismatchC>
            </Transplant>
        </Procedures>
    </ukrdc:PatientRecord>"""

    errors = validate_rda_xml_string(v4_00_transplant_xml, schema_version="4.0.0")
    assert not errors


def test_check_tests():
    """We need to ensure that cupid is always supporting the most recent
    version of the xsd schema.
    """

    # Grab all XML files in the tests directory and subdirectories
    # xml_files = glob.glob("tests/**/*.xml", recursive=True)
    xml_files = glob.glob("tests/xml_files/store_tests/*.xml")

    # Assuming you have a list of XML files, replace 'xml_files' with the actual list
    xml_strings = [open(xml_file).read() for xml_file in xml_files]

    # Select the maximum version from SUPPORTED_VERSIONS
    most_recent_version = max(SUPPORTED_VERSIONS)

    # Validate each XML string against the most recent supported version of the dataset
    clean = True
    for xml_file, xml_string in zip(xml_files, xml_strings):
        errors = validate_rda_xml_string(xml_string, schema_version=most_recent_version)

        # print errors if there are any
        if errors:
            for line, error in errors.items():
                print(xml_file)
                print(f"{line} - {error}")
                clean = False

    assert clean