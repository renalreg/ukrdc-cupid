"""
Models to create sqla objects from an xml file 
"""

from __future__ import annotations  # allows typehint of node class


import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session

from ukrdc_cupid.core.store.models.structure import Node

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
import ukrdc_xsdata.ukrdc.types as xsd_types  # type: ignore


class PatientNumber(Node):
    def __init__(self, xml: xsd_types.PatientNumber, seq_no: int):
        super().__init__(xml, sqla.PatientNumber, seq_no)

    def sqla_mapped() -> str:
        return "numbers"

    def map_xml_to_orm(self, _) -> None:
        self.add_item("patientid", self.xml.number)
        self.add_item("organization", self.xml.organization)
        self.add_item("numbertype", self.xml.number_type)


class Name(Node):
    def __init__(self, xml: xsd_types.Name, seq_no):
        super().__init__(xml, sqla.Name, seq_no)

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
    def __init__(self, xml: xsd_types.ContactDetail, seq_no: int):
        super().__init__(xml, sqla.ContactDetail, seq_no)

    def sqla_mapped() -> str:
        return "contact_details"

    def map_xml_to_orm(self, _) -> None:
        self.add_item("contactuse", self.xml.use)
        self.add_item("contactvalue", self.xml.value)
        self.add_item("commenttext", self.xml.comments)


class Address(Node):
    def __init__(self, xml: xsd_types.Address, seq_no: int):
        super().__init__(xml, sqla.Address, seq_no)

    def sqla_mapped() -> str:
        return "addresses"

    def map_xml_to_orm(self, session: Session) -> None:
        self.add_item("addressuse", self.xml.use)
        self.add_item("fromtime", self.xml.from_time)
        self.add_item("totime", self.xml.to_time)
        self.add_item("street", self.xml.street)
        self.add_item("town", self.xml.town)
        self.add_item("county", self.xml.county)
        self.add_item("postcode", self.xml.postcode)
        self.add_code("countrycode", "countrycodestd", "countrydesc", self.xml.country)

        self.updated_status(session)


class FamilyDoctor(Node):
    def __init__(self, xml: xsd_types.FamilyDoctor):
        super().__init__(xml, sqla.FamilyDoctor)

    def sqla_mapped() -> None:
        return None

    def generate_id(self) -> str:
        return self.pid

    def add_gp_address(self, xml: xsd_types.FamilyDoctor) -> None:
        if xml.address:
            self.add_item("addressuse", xml.address.use)
            self.add_item("fromtime", xml.address.from_time)
            self.add_item("totime", xml.address.to_time)
            self.add_item("street", xml.address.street)
            self.add_item("town", xml.address.town)
            self.add_item("county", xml.address.county)
            self.add_item("postcode", xml.address.postcode)
            if xml.country:
                self.add_code(
                    "countrycode", "countrycodestd", "countrydesc", xml.country
                )

    def add_gp_contact_detail(self, xml: xsd_types.FamilyDoctor) -> None:
        if xml.contact_detail:
            self.orm_object.contactuse = xml.country.use
            self.orm_object.contactvalue = xml.country.value
            self.orm_object.commenttext = xml.country.comments

    def map_xml_to_orm(self, session: Session) -> None:
        self.add_item("gpname", self.xml.gpname)
        self.add_item("gpid", self.xml.gpid)
        self.add_item("gppracticeid", self.xml.gppractice_id)
        self.add_item("email", self.xml.email)
        self.add_gp_address(self.xml)
        self.add_gp_contact_detail(self.xml)

        self.updated_status(session)


class Patient(Node):
    def __init__(self, xml: xsd_ukrdc.Patient):
        super().__init__(xml, sqla.Patient)

    def sqla_mapped() -> None:
        return None

    def generate_id(self) -> str:
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

        self.add_item("birthtime", self.xml.birth_time)
        self.add_item("deathtime", self.xml.death_time)
        self.add_item("gender", self.xml.gender)
        self.add_item("countryofbirth", self.xml.country_of_birth)
        self.add_code(
            "ethnicgroupcode",
            "ethnicgroupcodestd",
            "ethnicgroupdesc",
            self.xml.ethnic_group,
        )

        self.add_person_to_contact(self.xml.person_to_contact)
        self.add_code(
            "occupationcode", "occupationcodestd", "occupationdesc", self.xml.occupation
        )
        self.add_code(
            "primarylanguagecode",
            "primarylanguagecodestd",
            "primarylanguagedesc",
            self.xml.primary_language,
        )
        self.add_item("death", bool(self.xml.death))  # should this be optional?
        self.add_item(
            "updatedon", self.xml.updated_on
        )  # should this be automatically filled in by transform?
        self.add_item("bloodgroup", self.xml.blood_group)
        self.add_item("bloodrhesus", self.xml.blood_rhesus)

        # relationships these are all sequential
        self.add_children(
            PatientNumber, "patient_numbers.patient_number", session, True
        )
        self.add_children(Name, "names.name", session, True)
        self.add_children(
            ContactDetail, "contact_details.contact_detail", session, True
        )
        self.add_children(Address, "addresses.address", session, True)
        self.add_children(FamilyDoctor, "family_doctor", session)
