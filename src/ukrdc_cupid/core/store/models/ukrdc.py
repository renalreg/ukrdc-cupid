from __future__ import annotations  # allows typehint of node class
from abc import ABC, abstractmethod
from typing import Optional, Union

import ukrdc_cupid.core.store.keygen as key_gen
import ukrdc_xsdata.ukrdc as xsd_ukrdc
import ukrdc_xsdata.ukrdc.lab_orders as xsd_lab_orders
import ukrdc_sqla.ukrdc as sqla


import ukrdc_xsdata as xsd_all
from xsdata.models.datatype import XmlDateTime, XmlDate
import ukrdc_xsdata.ukrdc.types as xsd_types
import ukrdc_xsdata.ukrdc.social_histories as xsd_social_history  # noqa: F401
import ukrdc_xsdata.ukrdc.family_histories as xsd_family_history  # noqa: F401
import ukrdc_xsdata.ukrdc.allergies as xsd_allergy  # noqa: F401
import ukrdc_xsdata.ukrdc.diagnoses as xsd_diagnosis  # noqa: F401
import ukrdc_xsdata.ukrdc.medications as xsd_medication  # noqa: F401
import ukrdc_xsdata.ukrdc.procedures as xsd_procedure  # noqa: F401
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


class Node(ABC):
    """
    The xml files and the orm objects have a tree structure. This class is designed
    to abstract all of the idiocyncracies of the xml and the models into a class which
    contains everything needed to map a xml item to an sqla class. The nodes are explicitly
    mapped using the map_xml_to_tree function. The operations appied to the objects in the
    tree is recursively applied by the parent class.
    """

    def __init__(self, xml: xsd_all, orm_class: sqla = None, seq_no: int = None):
        self.xml = xml  # xml file corresponding to a given
        self.mapped_classes = []  # classes which depend on this one
        self.seq_no = seq_no  # should only be need for tables where there
        if not orm_class:
            raise NameError("orm_class must be specified in child class")

        # create orm object which maps to Node
        self.orm_object = orm_class()

    def add_item(
        self,
        property: str,
        value: Union[str, XmlDateTime, XmlDate, bool],
        optional: bool = True,
    ):
        """Function to update and item the ORM class instance based on xml.
        TODO: Do we need to think about type conversion to orm objects to the xml
        which are mostly strings? maybe this is most straightforwardly handled where
        it occurs in the xml_matching function.

        Args:
            property (str): _description_
            value (Union[str, XmlDateTime, xsd_types.Gender]): _description_
            optional (bool, optional): _description_. Defaults to True.
        """

        # add properties which constitute a single value
        # TODO: flag work item if non optional value doesn't exist
        if (optional and value) or (not optional):
            if value:
                if isinstance(value, (XmlDateTime, XmlDate)):
                    datetime = value.to_datetime()
                    setattr(self.orm_object, property, datetime)
                elif isinstance(value, (str, bool)):
                    setattr(self.orm_object, property, value)
                else:
                    setattr(self.orm_object, property, value.value)

    def add_code(
        self,
        property_code: str,
        property_std: str,
        property_description: str,
        xml_code: xsd_types.CodedField,
        optional=True,
    ):
        # add properties which are coded fields
        # TODO: flag an error/workitem if it doesn't exist?
        if (optional and xml_code) or (not optional):
            self.add_item(property_code, xml_code.code)
            self.add_item(property_description, xml_code.description)
            self.add_item(property_std, xml_code.coding_standard)

    def add_children(self, child_node: Node, xml_attr: str):

        # get xml items
        xml_items = getattr(self.xml, xml_attr, None)

        if xml_items:
            if not isinstance(xml_items, list):
                xml_items = [xml_items]

            for xml_item in xml_items:
                node = child_node(xml_item)
                node.map_xml_to_tree()
                self.mapped_classes.append(node)

    def transform(self, pid: str):
        """
        Abstraction to propagate transformation down through dependent classes
        """
        self.transformer(pid=pid)
        for child_class in self.mapped_classes:
            child_class.transformer(pid)

    def get_orm_list(self):
        """returns all the orm objects contained within the tree as a flat list as once we have transformed the orm objects trees are an unessarily awkward wase of space."""

        if self.mapped_classes:
            orm_objects = [self.orm_object]
            for child_class in self.mapped_classes:
                orm_objects = orm_objects + child_class.get_orm_list()
            return orm_objects
        else:
            return [self.orm_object]

    @abstractmethod
    def transformer(self, pid: Optional[str], **kwargs):
        """
        Specific to each class this will transform the data in the
        into the form required for the orm including adding keys, update dates etc

        Args:
            pid (Optional[str]): allows for a records containing pids
        """
        pass

    @abstractmethod
    def map_xml_to_tree(self):
        pass


class ResultItem(Node):
    def __init__(self, xml: xsd_lab_orders.ResultItem, seq_no: int = None):
        super().__init__(xml, sqla.ResultItem, seq_no)

    def map_xml_to_tree(self):
        self.add_item("prepost", self.xml.pre_post)
        self.add_item("interpretationcodes", self.xml.interpretation_codes)
        self.add_item("status", self.xml.status)
        self.add_item("resulttype", self.xml.result_type)
        self.add_item("enteredon", self.xml.entered_on)

        self.add_item("subid", self.xml.sub_id)
        self.add_item("resultvalue", self.xml.result_value)
        self.add_item("resultvalueunits", self.xml.result_value_units)
        self.add_item("referencerange", self.xml.reference_range)
        self.add_item("observationtime", self.xml.observation_time)
        self.add_item("commenttext", self.xml.comments)
        self.add_item("referencecomment", self.xml.reference_comment)

        self.add_code(
            "serviceidcode", "serviceidcodestd", "serviceiddesc", self.xml.service_id
        )

    def transformer(self, order_id: str, seq_no: int):
        self.orm_object.id = key_gen.generate_key_resultitem(
            self.orm_object, order_id=order_id, seq_no=seq_no
        )


class LabOrder(Node):
    def __init__(self, xml: xsd_lab_orders.LabOrder, seq_no: int = None):
        super().__init__(xml, sqla.LabOrder, seq_no)

    def map_xml_to_tree(self):

        self.add_item("placerid", self.xml.placer_id)
        self.add_item("fillerid", self.xml.filler_id)
        self.add_item("specimencollectedtime", self.xml.specimen_collected_time)
        self.add_item("status", self.xml.status)
        self.add_item("specimenreceivedtime", self.xml.specimen_received_time)

        self.add_item("specimensource", self.xml.specimen_source)
        self.add_item("duration", self.xml.duration)
        self.add_item("enteredon", self.xml.entered_on)
        self.add_item("updatedon", self.xml.updated_on)
        self.add_item("externalid", self.xml.external_id)

        self.add_code(
            "receivinglocationcode",
            "receivinglocationdesc",
            "receivinglocationcodestd",
            self.xml.receiving_location,
        )
        self.add_code(
            "orderedbycode", "orderedbycodestd", "orderedbydesc", self.xml.ordered_by
        )

        self.add_code(
            "orderitemcode", "orderitemcodestd", "orderitemdesc", self.xml.order_item
        )
        self.add_code(
            "ordercategorycode",
            "ordercategorycodestd",
            "ordercategorydesc",
            self.xml.order_category,
        )

        self.add_code(
            "prioritycode", "prioritycodestd", "prioritydesc", self.xml.priority
        )

        # self.add_patient_class(self.xml.patient_class)
        self.add_code(
            "patientclasscode",
            "pateintclassdesc",
            "patientclasscodestd",
            self.xml.patient_class,
        )

        self.add_code(
            "enteredatcode", "enteredatdesc", "enteredatcodestd", self.xml.entered_at
        )
        self.add_code(
            "enteringorganizationcode",
            "enteringorganizationcodestd",
            "enteringorganizationdesc",
            self.xml.entering_organization,
        )

        self.add_children(ResultItem, "result_items.result_item")

    def transform(self, pid):
        self.transformer(pid)
        for child_class in self.mapped_classes:
            child_class.transformer(
                child_class.orm_object,
                order_id=self.orm_object.order_id,
                seq_no=child_class.seq_no,
            )

    def transformer(self, pid):
        # we overwrite the base class because we result item needs extra info
        self.orm_object.pid = pid
        id = key_gen.generate_key_laborder(self.orm_object, pid)
        self.orm_object.id = id


class PatientNumber(Node):
    def __init__(self, xml: xsd_types.PatientNumber):
        super().__init__(xml, sqla.PatientNumber)

    def map_xml_to_tree(self):
        self.add_item("patientid", self.xml.number)
        self.add_item("organization", self.xml.organization)
        self.add_item("numbertype", self.xml.number_type)

    def transformer(self, pid):
        # TODO: look in java to find the correct way of generating the keys
        # figure out what to do with creation_date, idx, updatedon, actioncode,
        # externalid, update_date
        self.orm_object.pid = pid


class Name(Node):
    def __init__(self, xml: xsd_types.Name):
        super().__init__(xml, sqla.Name)

    def map_xml_to_tree(self):
        self.add_item("nameuse", self.xml.use)
        self.add_item("prefix", self.xml.prefix)
        self.add_item("family", self.xml.family)
        self.add_item("given", self.xml.given)
        self.add_item("othergivennames", self.xml.other_given_names)
        self.add_item("suffix", self.xml.suffix)

    def transformer(self, pid):
        self.orm_object.pid = pid


class ContactDetail(Node):
    def __init__(self, xml: xsd_types.ContactDetail):
        super().__init__(xml, sqla.ContactDetail)

    def map_xml_to_tree(self):
        self.add_item("contactuse", self.xml.use)
        self.add_item("contactvalue", self.xml.value)
        self.add_item("commenttext", self.xml.comments)

    def transformer(self, pid):
        self.orm_object.pid = pid


class Address(Node):
    def __init__(self, xml: xsd_types.Address):
        super().__init__(xml, sqla.Address)

    def map_xml_to_tree(self):
        self.add_item("addressuse", self.xml.use)
        self.add_item("fromtime", self.xml.from_time)
        self.add_item("totime", self.xml.to_time)
        self.add_item("street", self.xml.street)
        self.add_item("town", self.xml.town)
        self.add_item("county", self.xml.county)
        self.add_item("postcode", self.xml.postcode)
        self.add_code("countrycode", "countrycodestd", "countrydesc", self.xml.country)

    def transformer(self, pid):
        self.orm_object.pid = pid


class FamilyDoctor(Node):
    def __init__(self, xml: xsd_types.FamilyDoctor):
        super().__init__(xml, sqla.FamilyDoctor)

    def add_gp_address(self, xml: xsd_types.FamilyDoctor):
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

    def add_gp_contact_detail(self, xml: xsd_types.FamilyDoctor):
        if xml.contact_detail:
            self.orm_object.contactuse = xml.country.use
            self.orm_object.contactvalue = xml.country.value
            self.orm_object.commenttext = xml.country.comments

    def map_xml_to_tree(self):
        self.add_item("gpname", self.xml.gpname)
        self.add_item("gpid", self.xml.gpid)
        self.add_item("gppracticeid", self.xml.gppractice_id)
        self.add_item("email", self.xml.email)
        self.add_gp_address(self.xml)
        self.add_gp_contact_detail(self.xml)

    def transformer(self, pid):
        self.orm_object.pid = pid


class Patient(Node):
    """Initialise node for the patient object"""

    def __init__(self, xml: xsd_ukrdc.Patient):
        orm_class = sqla.Patient
        super().__init__(xml, orm_class)

    def add_person_to_contact(self, xml: xsd_types.PersonalContactType):
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

    def map_xml_to_tree(self):

        self.add_item("birthtime", self.xml.birth_time)
        self.add_item("deathtime", self.xml.death_time)
        self.add_item("gender", self.xml.gender)
        self.add_item("countryofbirth", self.xml.country_of_birth)
        self.add_code(
            "ethnicgroupcode",
            "ethnicgroupstd",
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

        # relationships
        self.add_children(PatientNumber, "patient_numbers.patient_number")
        self.add_children(Name, "names.name")
        self.add_children(ContactDetail, "contact_details.contact_detail")
        self.add_children(Address, "addresses.address")
        self.add_children(FamilyDoctor, "family_doctor")

    def transformer(self, pid: str):
        self.orm_object.pid = pid


class SocialHistory(Node):
    def __init__(self, xml: xsd_social_history.SocialHistory):
        super().__init__(xml, sqla.SocialHistory)

    def map_xml_to_tree(self):
        self.add_code(
            "socialhabitcode",
            "socialhabitcodestd",
            "socialhabitdesc",
            self.xml.social_habit,
            optional=False,
        )
        self.add_item("updatedon", self.xml.updated_on)
        self.add_item("externalid", self.xml.external_id)

    def transformer(self):
        pass


class FamilyHistory(Node):
    def __init__(self, xml: xsd_family_history.FamilyHistory):
        super().__init__(xml, sqla.FamilyHistory)

    def map_xml_to_tree(self):
        self.add_code(
            "familymembercode",
            "familymembercodestd",
            "familymemberdesc",
            self.xml.family_member,
            optional=False,
        )
        self.add_code(
            "diagnosiscode",
            "diagnosiscodingstandard",
            "diagnosisdesc",
            self.xml.diagnosis,
            optional=False,
        )
        self.add_item("notetext", self.xml.note_text)
        self.add_code(
            "enteredatcode",
            "enteredatcodestd",
            "enteredatdesc",
            self.xml.entered_at,
            optional=False,
        )
        self.add_item("fromtime", self.xml.from_time)
        self.add_item("totime", self.xml.to_time)
        self.add_item("updatedon", self.xml.updated_on)
        self.add_item("externalid", self.xml.external_id)

    def transformer(self):
        pass


class Allergy(Node):
    def __init__(self, xml: xsd_allergy.Allergy):
        super().__init__(xml, sqla.Allergy)

    def map_xml_to_tree(self):
        self.add_code(
            "allergycode",
            "allergycodestd",
            "allergydesc",
            self.xml.allergy,
            optional=False,
        )
        self.add_code(
            "allergycategorycode",
            "allergycategorycodestd",
            "allergycategorydesc",
            self.xml.allergy_category,
            optional=False,
        )
        self.add_code(
            "severitycode",
            "severitycodestd",
            "severitydesc",
            self.xml.severity,
            optional=False,
        )
        self.add_code(
            "cliniciancode", "cliniciancodestd", "cliniciandesc", self.xml.clinician
        )
        self.add_item("discoverytime", self.xml.discovery_time)
        self.add_item("confirmedtime", self.xml.confirmed_time)
        self.add_item("comments", self.xml.comments)
        self.add_item("inactivetime", self.xml.inactive_time)
        self.add_item("freetextallergy", self.xml.free_text_allergy)
        self.add_item("qualifyingdetails", self.xml.qualifying_details)

    def transformer(self):
        pass


class Diagnosis(Node):
    def __init__(self, xml: xsd_diagnosis.Diagnosis):
        super().__init__(xml, sqla.Diagnosis)

    def map_xml_to_tree(self):
        self.add_code(
            "diagnosingcliniciancode",
            "diagnosingcliniciancodestd",
            "diagnosingcliniciandesc",
            self.xml.diagnosing_clinician,
            optional=True,
        )

        self.add_code(
            "diagnosiscode",
            "diagnosiscodestd",
            "diagnosisdesc",
            self.xml.diagnosis,
            optional=True,
        )

        self.add_code(
            "enteredatcode",
            "enteredatcodestd",
            "enteredatdesc",
            self.xml.entered_at,
            optional=True,
        )

        self.add_item("diagnosistype", self.xml.diagnosis_type)
        self.add_item("comments", self.xml.comments)
        self.add_item("identificationtime", self.xml.identification_time)
        self.add_item("onsettime", self.xml.onset_time)
        self.add_item("enteredon", self.xml.entered_on)
        self.add_item("encounternumber", self.xml.encounter_number)
        self.add_item("verificationstatus", self.xml.verification_status)

    def transformer(self):
        pass


class CauseOfDeath(Node):
    def __init__(self, xml: xsd_diagnosis.CauseOfDeath):
        super().__init__(xml, sqla.CauseOfDeath)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class RenalDiagnosis(Node):
    def __init__(self, xml: xsd_diagnosis.RenalDiagnosis):
        super().__init__(xml, sqla.RenalDiagnosis)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class Medication(Node):
    def __init__(self, xml: xsd_diagnosis.RenalDiagnosis):
        super().__init__(xml, sqla.RenalDiagnosis)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class Procedure(Node):
    def __init__(self, xml: xsd_diagnosis.RenalDiagnosis):
        super().__init__(xml, sqla.RenalDiagnosis)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class DialysisSession(Node):
    def __init__(self, xml: xsd_diagnosis.RenalDiagnosis):
        super().__init__(xml, sqla.RenalDiagnosis)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class VascularAccess(Node):
    def __init__(self, xml: xsd_diagnosis.RenalDiagnosis):
        super().__init__(xml, sqla.RenalDiagnosis)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class Document(Node):
    def __init__(self, xml: xsd_diagnosis.RenalDiagnosis):
        super().__init__(xml, sqla.RenalDiagnosis)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class Encounter(Node):
    def __init__(self, xml: xsd_diagnosis.RenalDiagnosis):
        super().__init__(xml, sqla.RenalDiagnosis)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class Treatment(Node):
    def __init__(self, xml: xsd_encounters.Treatment):
        super().__init__(xml, sqla.Treatment)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class TransplantList(Node):
    def __init__(self, xml: xsd_encounters.TransplantList):
        super().__init__(xml, sqla.TransplantList)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class ProgramMembership(Node):
    def __init__(self, xml: xsd_program_memberships.ProgramMembership):
        super().__init__(xml, sqla.ProgramMembership)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class OptOut(Node):
    def __init__(self, xml: xsd_opt_outs.OptOut):
        super().__init__(xml, sqla.OptOut)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class ClinicalRelationship(Node):
    def __init__(self, xml: xsd_clinical_relationships.ClinicalRelationship):
        super().__init__(xml, sqla.ClinicalRelationship)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class PVData(Node):
    def __init__(self, xml):
        super().__init__(xml, sqla.PVData)

    def map_xml_to_tree(self):
        pass

    def transformer(self):
        pass


class PatientRecord(Node):
    def __init__(self, xml: xsd_ukrdc.PatientRecord):
        super().__init__(xml, sqla.PatientRecord)

    def map_xml_to_tree(self):
        self.add_item("sendingfacility", self.xml.sending_facility)
        self.add_item("sendingextract", self.xml.sending_extract)

        # map child objects
        self.add_children(Patient, "patient")

        self.add_children(LabOrder, "lab_orders.lab_order")
        self.add_children(SocialHistory, "social_histories.social_history")
        self.add_children(FamilyHistory, "family_histories.family_history")
        self.add_children(Allergy, "allergies.allergy")

        # diagnosis child objects
        self.add_children(Diagnosis, "diagnoses.diagnosis")

        # self.add_children(CauseOfDeath, "cause_of_death")
        # self.add_children(RenalDiagnosis, "renal_diagnosis")
        # self.add_children(Medication, self.xml.medication)
        # self.add_children(Procedure, self.xml.procedure)
        # self.add_children(DialysisSession, self.xml.dialysis_session)

        # self.add_children(VascularAccess, self.xml.vascular_access)
        # self.add_children(Document, self.xml.document)
        # self.add_children(Encounter, self.xml.encounter)
        # self.add_children(Treatment, self.xml.treatment)
        # self.add_children(TransplantList, self.xml.transplant_list)

        # self.add_children(ProgramMembership, self.xml.program_membership)
        # self.add_children(OptOut, self.xml.opt_out)
        # self.add_children(ClinicalRelationship, self.xml.clinical_realtionship)
        # self.add_children(PVData)

    def transformer(self, pid: str):
        self.orm_object.pid = pid
