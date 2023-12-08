from __future__ import annotations  # allows typehint of node class
from abc import ABC, abstractmethod
from typing import Optional, Union, List, Type
from decimal import Decimal

import ukrdc_cupid.core.store.keygen as key_gen  # type: ignore
import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from datetime import datetime
import warnings

import ukrdc_xsdata as xsd_all
from xsdata.models.datatype import XmlDateTime, XmlDate
import ukrdc_xsdata.ukrdc.types as xsd_types  # type: ignore

from pytz import timezone


class Node(ABC):
    """
    This class is basically designed to be a wrapper around the sqla classes which allows
    them to be mapped to incoming xml files and added to the database. In the spirit of ORM
    each table has a class associated to it which explicitly hardcodes all the idiocyncracies of
    both the xml file and the ukrdc datamodel.

    This Node class is something like a base class which contains the machinery to knit all of
    those table specific objects together. The patient record is treelike in structure so some of
    the methods work in a recursive way. The functions here as as generic as possible but not more
    so. This means in places they will have to be overidden.
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

    def generate_id(self) -> str:
        # Each database record has a natural key formed from compounding bits of information
        # the most common key appears to be pid (or parent record id) + enumeration of appearence in xml
        return key_gen.generate_generic_key(self.pid, self.seq_no)

    def map_to_database(self, session: Session, pid: str) -> str:
        # This is where we get really ORM. The function uses the primary key for the
        # record and loads the

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
        else:
            self.is_new_record = False

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
    ) -> None:
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
    ) -> None:
        """Function to do the mapping of a specific item from the xml file to the orm object. Since there are a varity of different items which can appear in the xml schema they.
        Args:
            sqla_property (str): This is basically the column name which is being set
            value (Union[str, XmlDateTime, XmlDate, bool, int, Decimal]): This is the xml which contains the value to set it with
            optional (bool, optional): This determines whether it is a required field or not
        """

        attr_persistant = getattr(self.orm_object, sqla_property)
        # parse value from xml into a python variable
        if (optional and value is not None) or (not optional):
            if value is not None:
                if isinstance(value, (XmlDateTime, XmlDate)):
                    # When the xml datetime parser does it's magic it will produce a time aware datetime
                    # The persistant datetimes are naive by default.
                    # To avoid issues when it comes to comparing them have to tell the datetime module that
                    # the persistant datetimes are assumed to be london.
                    if attr_persistant:
                        local_tz = timezone("Europe/London")
                        attr_persistant = local_tz.localize(attr_persistant)

                    attr_value = value.to_datetime()

                elif isinstance(value, (str, int, bool, Decimal)):
                    attr_value = value
                else:
                    attr_value = value.value

        else:
            # we over write property with null if it doesn't appear in the file
            attr_value = None

        # get persistant attribute and compare to incoming
        if attr_value != attr_persistant:
            setattr(self.orm_object, sqla_property, attr_value)
            self.is_modified = True

    def add_children(
        self,
        child_node: Type[Node],
        xml_attr: str,
        session: Session,
        sequential: bool = False,
    ) -> None:
        """Still not completely happy with this algorithm since it requires the
        objects to be added deleted explicitly rather than just being appended
        maybe this gives more control to fine tune the process. In principle we shouldn't
        need the recursive functions at all.

        Args:
            child_node (Type[Node]): _description_
            xml_attr (str): _description_
            session (Session): _description_
            sequential (bool, optional): _description_. Defaults to False.
        """

        # Step into the xml_file and extract the xml containing incoming data
        xml_items = self.xml
        for attr in xml_attr.split("."):
            if isinstance(xml_items, list):
                xml_items = xml_items[0]

            if xml_items:
                xml_items = getattr(xml_items, attr, None)

        mapped_ids = []
        if xml_items:
            if not isinstance(xml_items, list):
                # for convenience treat singular items as a list
                xml_items = [xml_items]

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

                # update new or existing using the
                node_object.map_xml_to_orm(session)

                # modify update_date and updated status
                node_object.updated_status(session)

                # append to parent
                self.mapped_classes.append(node_object)

        # if there are already objects mapped to record harmonise by deleting anything not in incoming
        sqla_relationship = child_node.sqla_mapped()
        if sqla_relationship:
            self.add_deleted(sqla_relationship, mapped_ids)

    def add_deleted(self, sqla_mapped: str, mapped_ids: List[str]) -> None:
        # stage records for deletion using the lazy mapping and a list of ids of records in the file
        # this is only needed if the is a one to many relationship between parent and child
        # this function stages for deletion objects which appear mapped but don't appear in incoming file
        # This highlights a problem with the idx method creating keys. What if an item in the middle of the
        # order gets deleted then everything below gets bumped up one.
        mapped_orms = getattr(self.orm_object, sqla_mapped)
        self.deleted_orm = [
            record for record in mapped_orms if record.id not in mapped_ids
        ]

    def get_orm_list(
        self, is_dirty: bool = False, is_new: bool = True, is_unchanged: bool = False
    ) -> List[sqla.Base]:
        """Utility function to return list of objects depending on their status.
        Theoretically all of this information should be in the session anyway.

        Args:
            is_dirty (bool, optional): _description_. Defaults to False.
            is_new (bool, optional): _description_. Defaults to True.
            is_unchanged (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """

        orm_objects = []

        # In normal operation we only need to explicitly add new records to session
        if self.is_new_record and is_new:
            orm_objects.append(self.orm_object)

        elif self.is_modified and is_dirty:
            orm_objects.append(self.orm_object)

        elif is_unchanged:
            orm_objects.append(self.orm_object)

        if self.mapped_classes:
            for child_class in self.mapped_classes:
                orm_objects = orm_objects + child_class.get_orm_list(
                    is_dirty, is_new, is_unchanged
                )

        return orm_objects

    def get_orm_deleted(self) -> List[sqla.Base]:
        # function to walk through the patient record structure an retrieve records staged for deletion
        if self.mapped_classes:
            orm_objects = self.deleted_orm
            for child_class in self.mapped_classes:
                orm_objects = orm_objects + child_class.get_orm_deleted()
            return orm_objects
        else:
            return self.deleted_orm

    def updated_status(self, session: Session) -> None:
        # function to update things like dates if object is changed
        # Personally I think this should all be moved to db triggers
        # Currently it will be null for new records
        # these type of changes should be made carefully to avoid churn

        if self.is_modified is True:
            self.orm_object.update_date = datetime.now()

    @abstractmethod
    def sqla_mapped():
        # if the parent class has a list like relationship to the Node this should be the name of that relationship
        # otherwise it should be None. In the case of a one to many relationship between parent and child this
        # is used to delete any associated objects which don't appear in the file.
        pass

    @abstractmethod
    def map_xml_to_orm(self, session: Session):
        # In this function all the idiosyncracies of the xml and the database are hard coded
        pass
