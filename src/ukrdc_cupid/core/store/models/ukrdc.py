"""
Models to create sqla objects from an xml file 
"""

from __future__ import annotations  # allows typehint of node class
from abc import ABC, abstractmethod, abstractproperty
from typing import Optional, Union, List, Type, Dict, Any
from decimal import Decimal

import ukrdc_cupid.core.store.keygen as key_gen  # type: ignore
import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
import ukrdc_xsdata.ukrdc.lab_orders as xsd_lab_orders  # type: ignore
import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from datetime import datetime
import warnings

import ukrdc_xsdata as xsd_all
from xsdata.models.datatype import XmlDateTime, XmlDate
import ukrdc_xsdata.ukrdc.types as xsd_types  # type: ignore
import ukrdc_xsdata.ukrdc.social_histories as xsd_social_history  # type: ignore
import ukrdc_xsdata.ukrdc.family_histories as xsd_family_history  # type: ignore
import ukrdc_xsdata.ukrdc.allergies as xsd_allergy  # type: ignore
import ukrdc_xsdata.ukrdc.diagnoses as xsd_diagnosis  # type: ignore
import ukrdc_xsdata.ukrdc.dialysis_prescriptions as xsd_prescriptions  # type: ignore
import ukrdc_xsdata.ukrdc.medications as xsd_medication  # type: ignore
import ukrdc_xsdata.ukrdc.procedures as xsd_procedure  # type: ignore
import ukrdc_xsdata.ukrdc.dialysis_sessions as xsd_dialysis_session  # type: ignore
import ukrdc_xsdata.ukrdc.transplants as xsd_transplants  # type: ignore
import ukrdc_xsdata.ukrdc.vascular_accesses as xsd_vascular_accesses  # type: ignore
import ukrdc_xsdata.ukrdc.encounters as xsd_encounters  # type: ignore
import ukrdc_xsdata.ukrdc.program_memberships as xsd_program_memberships  # type: ignore
import ukrdc_xsdata.ukrdc.opt_outs as xsd_opt_outs  # type: ignore
import ukrdc_xsdata.ukrdc.clinical_relationships as xsd_clinical_relationships  # type: ignore
import ukrdc_xsdata.ukrdc.surveys as xsd_surveys  # type: ignore
import ukrdc_xsdata.ukrdc.observations as xsd_observations  # type: ignore
import ukrdc_xsdata.ukrdc.documents as xsd_documents  # type: ignore

# import ukrdc_xsdata.pv.pv_2_0 as xsd_pvdata  # noqa: F401 type: ignore


class Node(ABC):
    """
    The xml files and the orm objects have a tree structure. This class is designed
    to abstract all of the idiocyncracies of the xml and the models into a class which
    contains everything needed to map a xml item to an sqla class. The nodes are explicitly
    mapped using the map_xml_to_tree function. The operations appied to the objects in the
    tree is recursively applied by the parent class.
    """

    def __init__(
        self,
        xml: xsd_all,
        orm_model: sqla.Base,  # type:ignore
        seq_no: Optional[int] = None,
    ):
        self.xml = xml  # xml file corresponding to a given
        self.mapped_classes: List[Node] = []  # classes which depend on this one
        self.deleted_orm: List[sqla.Base] = []  # records staged for deletion
        self.seq_no = seq_no  # should only be need for tables where there is no unique set of varibles
        self.orm_model = orm_model  # orm class
        self.is_new_record: bool = True  # flag if record is new to database
        self.is_modified: bool = False
        self.sqla_mapped: Optional[
            str
        ] = None  # This holds the attribute of the lazy mapping in sqla i.e [mapped children] = getter(parent orm, self.sqla_mapped)
        self.pid: Optional[str] = None  # placeholder for pid

    def generate_id(self):
        # compound whatever we need to identify object
        return key_gen.generate_generic_key(self.pid, self.seq_no)

    def map_to_database(self, session: Session, pid: str):
        self.pid = pid
        id = self.generate_id()

        # Use primary key to fetch record
        self.orm_object = session.get(self.orm_model, id)

        # If it doesn't exit create it and flag that you have done that
        # if it needs a pid add it to the orm
        if self.orm_object is None:
            self.orm_object = self.orm_model(id=id)
            self.is_new_record = True
            if hasattr(self.orm_object, "pid"):
                self.orm_object.pid = pid

        if self.seq_no is not None:
            self.orm_object.idx = self.seq_no

        return id

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

    def add_item(
        self,
        sqla_property: str,
        value: Union[str, XmlDateTime, XmlDate, bool, int, Decimal],
        optional: bool = True,
    ):
        """Function to do the mapping of a specific item from the xml file to the orm object. Since there are a varity of different items which can appear in the xml schema they.
        Args:
            sqla_property (str): This is basically the column name which is being set
            value (Union[str, XmlDateTime, XmlDate, bool, int, Decimal]): This is the xml which contains the value to set it with
            optional (bool, optional): This determines whether it is a required field or not
        """

        # add properties which constitute a single value
        # TODO: flag work item if non optional value doesn't exist
        if (optional and value is not None) or (not optional):
            if value is not None:
                if isinstance(value, (XmlDateTime, XmlDate)):
                    datetime = value.to_datetime()
                    setattr(self.orm_object, sqla_property, datetime)
                elif isinstance(value, (str, int, bool, Decimal)):
                    setattr(self.orm_object, sqla_property, value)
                else:
                    setattr(self.orm_object, sqla_property, value.value)
        else:
            # we over write property with null if it doesn't appear in the file
            setattr(self.orm_object, sqla_property, None)
            if value is not None and getattr(self.orm_object, sqla_property) is None:
                # will this ever actually get triggered?
                warnings.warn(f"Property {sqla_property} not added to ORM")

    def add_children(
        self,
        child_node: Type[Node],
        xml_attr: str,
        session: Session,
        sequential: bool = False,
    ):

        # Step into the xml_file and extract the xml containing incoming data
        xml_items = self.xml
        for attr in xml_attr.split("."):
            if isinstance(xml_items, list):
                xml_items = xml_items[0]

            if xml_items:
                xml_items = getattr(xml_items, attr, None)

        if xml_items:
            if not isinstance(xml_items, list):
                # for convenience treat singular items as a list
                xml_items = [xml_items]

            mapped_ids = []
            for seq_no, xml_item in enumerate(xml_items):
                # Some item are sent in sequential order this order implicitly sets the keys
                # there is a possibility here to sort the items before enumerating them
                if sequential:
                    node_object = child_node(xml=xml_item, seq_no=seq_no)
                else:
                    node_object = child_node(xml=xml_item)  # type:ignore

                # map to existing object or create new
                id = node_object.map_to_database(session, self.pid)
                mapped_ids.append(id)

                # update node from xml and add to collection
                node_object.map_xml_to_orm(session)

                # currently we add all objects regardless of status sqla flush should be able to detect changes
                self.mapped_classes.append(node_object)

            # stage records for deletion
            self.add_deleted(node_object.sqla_mapped, mapped_ids)

    def add_deleted(self, sqla_mapped: str, mapped_ids: List[str]):
        # stage records for deletion using the lazy mapping and a list of ids of records in the file
        # this is only needed if the is a one to many relationship between parent and child
        # this function stages for deletion objects which appear mapped but don't appear in incoming file
        # This highlights a problem with the idx method creating keys. What if an item in the middle of the
        # order gets deleted then everything below gets bumped up one.
        mapped_orms = getattr(self.orm_object, sqla_mapped)
        if isinstance(mapped_orms, list):
            self.deleted_orm = [
                record
                for record in getattr(self.orm_object, sqla_mapped)
                if record.id not in mapped_ids
            ]
        else:
            self.deleted_orm = []

    def get_orm_list(self):
        """returns all the orm objects contained within the tree as a flat list as once we have transformed the orm objects trees are an unessarily awkward wase of space."""

        if self.mapped_classes:
            orm_objects = [self.orm_object]
            for child_class in self.mapped_classes:
                orm_objects = orm_objects + child_class.get_orm_list()
            return orm_objects
        else:
            return [self.orm_object]

    def get_orm_deleted(self):
        if self.mapped_classes:
            orm_objects = self.deleted_orm
            for child_class in self.mapped_classes:
                orm_objects = orm_objects + child_class.get_orm_deleted()
            return orm_objects
        else:
            return self.deleted_orm

    def updated_status(self, session: Session):
        # function to update things like dates if object is changed
        # Personally I think this should all be moved to db triggers
        # Currently it will be null for new records
        # these type of changes should be made carefully to avoid churn

        # if not self.is_new_record:
        self.is_modified = session.is_modified(self.orm_object)
        if self.is_modified is True:
            print(self.orm_object.__tablename__)
            self.orm_object.update_date = datetime.now()

    @abstractmethod
    def map_xml_to_orm(self, session: Session):
        # bread and butter function the does all the painstaking mapping
        pass


class Observation(Node):
    def __init__(self, xml: xsd_observations.Observation, seq_no: int):
        super().__init__(xml, sqla.Observation, seq_no)
        self.sqla_mapped = "observations"

    def map_xml_to_orm(self, session: Session):

        # fmt: off
        self.add_item("observationtime", self.xml.observation_time, optional=False)
        self.add_code("observationcode", "observationcodestd", "observationdesc", self.xml.observation_code, optional=True)
        self.add_item("observationvalue", self.xml.observation_value, optional=True)
        self.add_item("observationunits", self.xml.observation_units, optional=True)
        self.add_item("prepost", self.xml.pre_post, optional=True)
        self.add_item("commenttext", self.xml.comments, optional=True)

        self.add_code("enteredatcode", "enteredatcodestd", "enteredatdesc", self.xml.entered_at, optional=True)
        self.add_code("enteringorganizationcode", "enteringorganizationcodestd", "enteringorganizationdesc", self.xml.entering_organization, optional=True)
        self.add_item("updatedon", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)
        # fmt: on

        self.updated_status(session)


class PatientNumber(Node):
    def __init__(self, xml: xsd_types.PatientNumber, seq_no: int):
        super().__init__(xml, sqla.PatientNumber, seq_no)
        self.sqla_mapped = "numbers"

    def map_xml_to_orm(self, session: Session):
        self.add_item("patientid", self.xml.number)
        self.add_item("organization", self.xml.organization)
        self.add_item("numbertype", self.xml.number_type)

        self.updated_status(session)


class Name(Node):
    def __init__(self, xml: xsd_types.Name, seq_no):
        super().__init__(xml, sqla.Name, seq_no)
        self.sqla_mapped = "names"

    def map_xml_to_orm(self, session: Session):
        self.add_item("nameuse", self.xml.use)
        self.add_item("prefix", self.xml.prefix)
        self.add_item("family", self.xml.family)
        self.add_item("given", self.xml.given)
        self.add_item("othergivennames", self.xml.other_given_names)
        self.add_item("suffix", self.xml.suffix)

        self.updated_status(session)


class ContactDetail(Node):
    def __init__(self, xml: xsd_types.ContactDetail, seq_no: int):
        super().__init__(xml, sqla.ContactDetail, seq_no)
        self.sqla_mapped = "contact_details"

    def map_xml_to_orm(self, session: Session):
        self.add_item("contactuse", self.xml.use)
        self.add_item("contactvalue", self.xml.value)
        self.add_item("commenttext", self.xml.comments)

        self.updated_status(session)


class Address(Node):
    def __init__(self, xml: xsd_types.Address, seq_no: int):
        super().__init__(xml, sqla.Address, seq_no)
        self.sqla_mapped = "addresses"

    def map_xml_to_orm(self, session: Session):
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
        self.sqla_mapped = "familydoctor"

    def generate_id(self):
        return self.pid

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

    def map_xml_to_orm(self, session: Session):
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
        self.sqla_mapped = "patient"

    def generate_id(self):
        return self.pid

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

    def map_xml_to_orm(self, session: Session):

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


class PatientRecord(Node):
    def __init__(self, xml: xsd_ukrdc.PatientRecord):
        super().__init__(xml, sqla.PatientRecord)

        # some records have an additional date (aside from the usual ones update by db triggers)
        # we will now use this to host the date that gets sent on the sending facility
        self.repository_updated_date = xml.sending_facility.time.to_datetime()

        if xml.lab_orders:
            self.lab_order_range = [
                xml.lab_orders.start.to_datetime(),
                xml.lab_orders.stop.to_datetime(),
            ]

        if xml.observations:
            self.observations = [
                xml.observations.start.to_datetime(),
                xml.observations.stop.to_datetime(),
            ]

    def updated_status(self, session: Session):
        super().updated_status(session)
        if self.is_new_record:
            self.orm_object.repositorycreationdate = self.repository_updated_date

        if self.is_modified or self.is_new_record:
            # what is the correct behaviour should this be set if any part of the patient record has been changed?
            # I think this should be a nullable field
            self.orm_object.repositoryupdatedate = self.repository_updated_date

    def map_xml_to_orm(self, session: Session):

        # core patient record
        self.add_item("sendingfacility", self.xml.sending_facility)
        self.add_item("sendingextract", self.xml.sending_extract)

        # get MRN from patient numbers model
        for number in self.xml.patient.patient_numbers[0].patient_number:
            if number.number_type.value == "MRN":
                self.orm_object.localpatientid = number.number

        self.add_children(Patient, "patient", session)
        self.add_children(Observation, "observations.observation", session, True)

        self.updated_status(session)

    def map_to_database(self, pid: str, ukrdcid: str, session: Session, is_new=True):
        self.pid = pid
        self.session = session
        self.is_new_record = is_new

        # load or create the orm
        if is_new:
            self.orm_object = self.orm_model(pid=self.pid, ukrdcid=ukrdcid)
        else:
            self.orm_object = session.get(self.orm_model, self.pid)

        self.map_xml_to_orm(session)

    def get_orm_deleted(self):
        # probably don't want to stage patient record for deletion
        orm_objects = []
        for child_class in self.mapped_classes:
            orm_objects = orm_objects + child_class.get_orm_deleted()

        return orm_objects
