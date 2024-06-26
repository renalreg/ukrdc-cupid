"""
Models to create sqla objects from an xml file 
"""

from __future__ import annotations  # allows typehint of node class


import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session

from ukrdc_cupid.core.store.models.structure import Node

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
import ukrdc_xsdata.ukrdc.types as xsd_types  # type: ignore
import ukrdc_xsdata.ukrdc.allergies as xsd_allergy  # type: ignore
import ukrdc_xsdata.ukrdc.diagnoses as xsd_diagnosis  # type: ignore
import ukrdc_xsdata.ukrdc.surveys as xsd_surveys  # type: ignore
import ukrdc_xsdata.ukrdc.family_histories as xsd_family_histories

# import ukrdc_xsdata.ukrdc


def add_address(node: Node, address_xml: xsd_types.Address):
    # fmt: off
    node.add_item("addressuse", address_xml.use)
    node.add_item("fromtime", address_xml.from_time)
    node.add_item("totime", address_xml.to_time)
    node.add_item("street", address_xml.street)
    node.add_item("town", address_xml.town)
    node.add_item("county", address_xml.county)
    node.add_item("postcode", address_xml.postcode)
    node.add_code("countrycode", "countrycodestd", "countrydesc", address_xml.country)
    # fmt: on


class PatientNumber(Node):
    def __init__(self, xml: xsd_types.PatientNumber):
        super().__init__(xml, sqla.PatientNumber)

    def sqla_mapped() -> str:
        return "numbers"

    def map_xml_to_orm(self, _) -> None:
        self.add_item("patientid", self.xml.number)
        self.add_item("organization", self.xml.organization)
        self.add_item("numbertype", self.xml.number_type)


class Name(Node):
    def __init__(self, xml: xsd_types.Name):
        super().__init__(xml, sqla.Name)

    def sqla_mapped() -> str:
        return "names"

    def map_xml_to_orm(self, _) -> None:
        self.add_item("nameuse", self.xml.use)
        self.add_item("prefix", self.xml.prefix)
        self.add_item("family", self.xml.family)
        self.add_item("given", self.xml.given)
        self.add_item("othergivennames", self.xml.other_given_names)
        self.add_item("suffix", self.xml.suffix)


class ContactDetail(Node):
    def __init__(self, xml: xsd_types.ContactDetail):
        super().__init__(xml, sqla.ContactDetail)

    def sqla_mapped() -> str:
        return "contact_details"

    def map_xml_to_orm(self, _) -> None:
        self.add_item("contactuse", self.xml.use)
        self.add_item("contactvalue", self.xml.value)
        self.add_item("commenttext", self.xml.comments)


class Address(Node):
    def __init__(self, xml: xsd_types.Address):
        super().__init__(xml, sqla.Address)

    def sqla_mapped() -> str:
        return "addresses"

    def map_xml_to_orm(self, _) -> None:
        # reused function elsewhere
        add_address(self, self.xml)


class FamilyDoctor(Node):
    def __init__(self, xml: xsd_types.FamilyDoctor):
        super().__init__(xml, sqla.FamilyDoctor)

    def sqla_mapped() -> None:
        return None

    def generate_id(self, _) -> str:
        return self.pid

    def add_gp_contact_detail(self, xml: xsd_types.FamilyDoctor) -> None:
        if xml.contact_detail:
            self.orm_object.contactuse = xml.contact_detail.use.value
            self.orm_object.contactvalue = xml.contact_detail.value
            self.orm_object.commenttext = xml.contact_detail.comments

    def map_xml_to_orm(self, session: Session) -> None:
        self.add_item("gpname", self.xml.gpname)
        self.add_item("gpid", self.xml.gpid)
        self.add_item("gppracticeid", self.xml.gppractice_id)
        self.add_item("email", self.xml.email)
        if self.xml.address:
            add_address(self, self.xml.address)

        self.add_gp_contact_detail(self.xml)


class Patient(Node):
    def __init__(self, xml: xsd_ukrdc.Patient):
        super().__init__(xml, sqla.Patient)

    def sqla_mapped() -> None:
        return None

    def generate_id(self, _) -> str:
        return self.pid

    def add_person_to_contact(self, xml: xsd_types.PersonalContactType) -> None:
        # handle section of xml which the generic add functions cant handle
        if xml:
            self.orm_object.persontocontactname = xml.name
            self.orm_object.persontocontact_relationship = xml.relationship
            if xml.contact_details:
                # TODO: convince myself the getting the first contact details is correct
                self.orm_object.persontocontact_contactnumber = (
                    self.xml.contact_details[0].value
                )
                self.orm_object.persontocontact_contactnumbercomments = (
                    self.xml.contact_details[0].comments
                )
                self.orm_object.persontocontact_contactnumbertype = (
                    self.xml.contact_details[0].use
                )

    def map_xml_to_orm(self, session: Session) -> None:
        # fmt: off
        self.add_item("birthtime", self.xml.birth_time)
        self.add_item("deathtime", self.xml.death_time)
        self.add_item("gender", self.xml.gender)
        self.add_item("countryofbirth", self.xml.country_of_birth)
        self.add_code("ethnicgroupcode","ethnicgroupcodestd","ethnicgroupdesc",self.xml.ethnic_group)

        self.add_person_to_contact(self.xml.person_to_contact)
        self.add_code( "occupationcode", "occupationcodestd", "occupationdesc", self.xml.occupation)
        self.add_code("primarylanguagecode","primarylanguagecodestd","primarylanguagedesc", self.xml.primary_language)
        self.add_item("death", bool(self.xml.death))  # should this be optional?
        self.add_item("updatedon", self.xml.updated_on)  # should this be automatically filled in by transform?
        self.add_item("bloodgroup", self.xml.blood_group)
        self.add_item("bloodrhesus", self.xml.blood_rhesus)

        # relationships these are all sequential
        self.add_children(PatientNumber, "patient_numbers.patient_number", session)
        self.add_children(Name, "names.name", session)
        self.add_children(ContactDetail, "contact_details.contact_detail", session)
        self.add_children(Address, "addresses.address", session)
        self.add_children(FamilyDoctor, "family_doctor", session)
        # fmt: on


class SocialHistory(Node):
    def __init__(self, xml: xsd_ukrdc.Patient):
        super().__init__(xml, sqla.SocialHistory)

    def sqla_mapped() -> str:
        return "social_histories"

    def map_xml_to_orm(self, _):
        # fmt:off
        self.add_code("socialhabitcode", "socialhabitcodestd", "socialhabitdesc", self.xml.social_habit, optional=False)
        self.add_item("updatedon", self.xml.updated_on)
        self.add_item("externalid", self.xml.external_id)
        # fmt:on


class FamilyHistory(Node):
    def __init__(self, xml: xsd_family_histories):
        super().__init__(xml, sqla.FamilyHistory)

    def sqla_mapped() -> str:
        return "family_histories"

    def map_xml_to_orm(self, _):
        # fmt: off
        self.add_code("familymembercode", "familymembercodestd", "familymemberdesc", self.xml.family_member, optional=True)
        self.add_code("diagnosiscode", "diagnosiscodestd", "diagnosisdesc", self.xml.diagnosis, optional=True)
        self.add_item("notetext", self.xml.note_text, optional=True)
        self.add_code("enteredatcode", "enteredatcodestd", "enteredatdesc", self.xml.entered_at, optional=True)
        self.add_item("fromtime", self.xml.from_time, optional=True)
        self.add_item("totime", self.xml.to_time, optional=True)
        self.add_item("updatedon", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)        
        # fmt: on


class Allergy(Node):
    def __init__(self, xml: xsd_allergy.Allergy):
        super().__init__(xml, sqla.Allergy)

    def sqla_mapped() -> str:
        return "allergies"

    def map_xml_to_orm(self, _):
        # fmt: off
        self.add_code("allergycode","allergycodestd","allergydesc", self.xml.allergy)
        self.add_code("allergycategorycode","allergycategorycodestd","allergycategorydesc", self.xml.allergy_category)
        self.add_code("severitycode","severitycodestd","severitydesc", self.xml.severity)
        self.add_code("cliniciancode","cliniciancodestd","cliniciandesc",self.xml.clinician)
        self.add_item("discoverytime", self.xml.discovery_time, optional=True)
        self.add_item("confirmedtime", self.xml.confirmed_time, optional=True)
        self.add_item("comments", self.xml.comments, optional=True)
        self.add_item("inactivetime", self.xml.inactive_time, optional=True)
        self.add_item("freetextallergy", self.xml.free_text_allergy, optional=True)
        self.add_item("qualifyingdetails", self.xml.qualifying_details, optional=True)

        # common metadata
        self.add_item("updatedon", self.xml.updated_on, optional=True)

        # there is an update_date, actioncode here not sure what it does
        self.add_item("externalid", self.xml.external_id, optional=True)
        # fmt: on


class Diagnosis(Node):
    def __init__(self, xml: xsd_diagnosis.Diagnosis):
        super().__init__(xml, sqla.Diagnosis)

    def sqla_mapped() -> str:
        return "diagnoses"

    def map_xml_to_orm(self, _):
        # fmt: off
        self.add_code("diagnosingcliniciancode", "diagnosingcliniciancodestd", "diagnosingcliniciandesc", self.xml.diagnosing_clinician)

        self.add_code("diagnosiscode", "diagnosiscodestd", "diagnosisdesc", self.xml.diagnosis)

        # TODO: Add biopsy performed when supported by the database.
        self.add_item("diagnosistype", self.xml.diagnosis_type)
        self.add_item("comments", self.xml.comments)
        self.add_item("identificationtime", self.xml.identification_time)
        self.add_item("onsettime", self.xml.onset_time)
        self.add_item("enteredon", self.xml.entered_on)
        self.add_item("encounternumber", self.xml.encounter_number)
        self.add_item("verificationstatus", self.xml.verification_status)

        # common metadata
        self.add_item("updatedon", self.xml.updated_on)
        self.add_item("externalid", self.xml.external_id)
        # fmt: on


class RenalDiagnosis(Node):
    def __init__(self, xml: xsd_diagnosis.RenalDiagnosis):
        super().__init__(xml, sqla.RenalDiagnosis)

    def sqla_mapped() -> str:
        return "renaldiagnoses"

    def map_xml_to_orm(self, _):
        # fmt: off
        self.add_item("diagnosistype", self.xml.diagnosis_type)
        self.add_code( "diagnosingcliniciancode", "diagnosingcliniciancodestd", "diagnosingcliniciandesc", self.xml.diagnosing_clinician)
        self.add_code("diagnosiscode", "diagnosiscodestd","diagnosisdesc", self.xml.diagnosis)
        self.add_item("comments", self.xml.comments)
        self.add_item("identificationtime", self.xml.identification_time)
        self.add_item("onsettime", self.xml.onset_time)
        self.add_item("enteredon", self.xml.entered_on)

        # common metadata
        self.add_item("updatedon", self.xml.updated_on)
        self.add_item("externalid", self.xml.external_id)

        if self.xml.verification_status:
            print("Cause of Death verification status not currently supported")

        if self.xml.biopsy_performed:
            print("Biopsy performed status not currently supported")
        # fmt: on


class CauseOfDeath(Node):
    def __init__(self, xml: xsd_diagnosis.CauseOfDeath):
        super().__init__(xml, sqla.CauseOfDeath)

    def sqla_mapped() -> str:
        return "cause_of_death"

    def map_xml_to_orm(self, _):
        # fmt: off
        self.add_item("diagnosistype", self.xml.diagnosis_type)
        self.add_code("diagnosiscode", "diagnosiscodestd", "diagnosisdesc", self.xml.diagnosis)

        self.add_item("comments", self.xml.comments, optional=True)
        self.add_item()
        self.add_item("enteredon", self.xml.entered_on, optional=True)

        # common metadata
        self.add_item("updatedon", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)
        # fmt: on


class Document(Node):
    def __init__(self, xml: xsd_diagnosis.Diagnosis):
        super().__init__(xml, sqla.Document)

    def sqla_mapped() -> str:
        return "documents"

    def map_xml_to_orm(self, orm_object):
        self.add_code(
            "cliniciancode", "cliniciancodestd", "cliniciandesc", self.xml.clinician
        )
        self.add_item("documentname", self.xml.document_name)
        self.add_item("documenttime", self.xml.document_time)
        self.add_code(
            "documenttypecode",
            "documenttypecodestd",
            "documenttypedesc",
            self.xml.document_type,
        )
        self.add_item("documenturl", self.xml.document_url)
        self.add_code(
            "enteredatcode", "enteredatcodestd", "enteredatdesc", self.xml.entered_at
        )
        self.add_code(
            "enteredbycode", "enteredbycodestd", "enteredbydesc", self.xml.entered_by
        )
        self.add_item("externalid", self.xml.external_id, optional=True)
        self.add_item("filename", self.xml.file_name)
        self.add_item("filetype", self.xml.file_type)
        self.add_item("notetext", self.xml.note_text)
        self.add_code("statuscode", "statuscodestd", "statusdesc", self.xml.status)
        # not sure exactly what's going on here. I think the purpose of this
        # field is to store the document as binary. The xsdata models seem to
        # decode it automatically. Probably it then gets encoded again
        if self.xml.stream:
            self.orm_object.stream = self.xml.stream
            print(":)")

        # self.add_item("stream", int(self.xml.stream))
        self.add_item("updatedon", self.xml.updated_on, optional=True)


class Survey(Node):
    def __init__(self, xml: xsd_surveys.Survey):
        super().__init__(xml, sqla.Survey)

    def sqla_mapped() -> str:
        return "surveys"

    def map_xml_to_orm(self, _):
        pass


class Score(Node):
    def __init__(self, xml: xsd_surveys.Score):
        super().__init__(xml, sqla.Score)

    def sqla_mapped() -> str:
        return "scores"

    def map_xml_to_orm(self, _):
        pass


class Question(Node):
    def __init__(self, xml: xsd_surveys.Question):
        super().__init__(xml, sqla.Question)

    def sqla_mapped() -> str:
        return "questions"

    def map_xml_to_orm(self, _):
        pass
