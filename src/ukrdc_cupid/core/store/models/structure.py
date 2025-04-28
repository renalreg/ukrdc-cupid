from __future__ import annotations  # allows typehint of node class
from abc import ABC, abstractmethod
from typing import Optional, Union, List, Type
from decimal import Decimal
from enum import Enum, auto

import csv
import ukrdc_cupid.core.store.keygen as key_gen
import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

import ukrdc_xsdata as xsd_all  # type:ignore
from xsdata.models.datatype import XmlDateTime, XmlDate
import ukrdc_xsdata.ukrdc.types as xsd_types  # type: ignore

from pytz import timezone

class RecordStatus(Enum):
    NEW = auto()
    MODIFIED = auto()
    UNCHANGED = auto()

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
    ):
        self.xml = xml  # xml file corresponding to a given
        self.mapped_classes: List[Node] = []  # classes which depend on this one
        self.deleted_orm: List[sqla.Base] = []  # type:ignore
        self.orm_model = orm_model  # orm class
        self.pid: Optional[str] = None  # placeholder for pid
        self.status: RecordStatus = RecordStatus.UNCHANGED

    def generate_id(self, seq_no: int) -> str:
        # Each database record has a natural key formed from compounding bits of information
        # the most common key appears to be pid (or parent record id) + enumeration of appearence in xml

        if self.pid is not None:
            id = key_gen.generate_generic_key(self.pid, seq_no)
        else:
            id = str(seq_no)
        return id

    def map_to_database(
        self, session: Session, pid: Union[str, None], seq_no: int
    ) -> str:

        self.pid = pid
        id = self.generate_id(seq_no)

        # Use primary key to fetch record
        self.orm_object = session.get(self.orm_model, id)

        # If it doesn't exit create it and flag that it's new
        if self.orm_object is None:
            self.orm_object = self.orm_model(id=id)  # type:ignore
            self.status = RecordStatus.NEW

        return id

    def add_code(
        self,
        property_code: str,
        property_std: str,
        property_description: str,
        xml_code: xsd_types.CodedField,
        optional: bool = True,
    ) -> None:
        # add properties which are coded fields really I could have saved
        # myself a lot of work if I had written a function like this for
        # each of the types that get repeatedly reused in the schema. For
        # example, common metadata appears in almost every table and is
        # currently hard coded

        if (optional and xml_code) or (not optional):
            self.add_item(property_code, xml_code.code)
            self.add_item(property_description, xml_code.description)
            self.add_item(property_std, xml_code.coding_standard)
        else:
            # this block ensures value gets blanked if its in the orm but not
            # in incoming code
            self.add_item(property_code, None)
            self.add_item(property_description, None)
            self.add_item(property_std, None)

    def add_item(
        self,
        sqla_property: str,
        value: Optional[Union[str, XmlDateTime, XmlDate, bool, int, Decimal]],
        optional: bool = True,
    ) -> None:
        """Function to do the mapping of a specific item from the xml file to the orm object. Since there are a varity of different items which can appear in the xml schema they.
        Args:
            sqla_property (str): This is basically the column name which is being set
            value (Union[str, XmlDateTime, XmlDate, bool, int, Decimal]): This is the xml which contains the value to set it with
            optional (bool, optional): This determines whether it is a required field or not
        """

        attr_value: Union[str, int, bool, Decimal, datetime, None]
        attr_persist = getattr(self.orm_object, sqla_property)
        # parse value from xml into a python variable
        if (optional and value is not None) or (not optional):
            if value is not None:
                if isinstance(value, (XmlDateTime, XmlDate)):
                    # When the xml datetime parser does it's magic it will produce a time aware datetime
                    # The persistent datetimes are naive by default.
                    # To avoid issues when it comes to comparing them have to tell the datetime module that
                    # the persistant datetimes are assumed to be london.
                    if attr_persist:
                        if isinstance(attr_persist, datetime):
                            local_tz = timezone("Europe/London")
                            attr_persist = local_tz.localize(attr_persist)

                    attr_value = value.to_datetime()

                elif isinstance(value, (str, int, bool, Decimal)):
                    attr_value = value
                else:
                    attr_value = value.value

        else:
            # we over write property with null if it doesn't appear in the file
            attr_value = None

        # get persistant attribute and compare to incoming
        if attr_value != attr_persist:
            setattr(self.orm_object, sqla_property, attr_value)
            if self.status != RecordStatus.NEW:
                self.status = RecordStatus.MODIFIED

    def add_children(
        self, child_node: Type[Node], xml_attr: str, session: Session
    ) -> None:
        """Still not completely happy with this algorithm since it requires the
        objects to be added and deleted explicitly rather than just being
        appended although maybe this gives more control to fine tune the
        process. The complexity here is allows the process which is general,
        for and example of how it would work without the generalisation look
        at the laborder, and result items where these methods have been
        overwritten.

        Args:
            child_node (Type[Node]): _description_
            xml_attr (str): _description_
            session (Session): _description_
            sequential (bool, optional): _description_. Defaults to False.
        """

        # Blank xml
        # is_empty = len(xml_items)

        # Step into the xml_file and extract the xml containing incoming data
        xml_items = self.xml
        for attr in xml_attr.split("."):
            # This pattern is used where the xml looks something like
            # <Procedures>
            #    <Treatment>
            #    </Treatment>
            # </Procedures>
            # with the ultimate goal of just creating a list of bits of xml
            # whose attributes correspond specifically to attributes of a
            # ukrdc_sqla model
            if isinstance(xml_items, list):
                # this is necessary because of the weirdness of xsdata
                if xml_items:
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
                node_object = child_node(xml=xml_item)  # type:ignore

                # Generate parent data also required for setting primary keys
                parent_data = self.generate_parent_data(seq_no)

                # map to existing object or create new
                id = node_object.map_to_database(session, self.pid, seq_no)
                mapped_ids.append(id)

                # add parent info
                # add any foreign keys, enumerations or data which doesn't come
                # from the xml.
                for attr, value in parent_data.items():
                    if hasattr(node_object.orm_object, attr):
                        setattr(node_object.orm_object, attr, value)

                # update new or existing using the
                node_object.map_xml_to_orm(session)

                # modify update_date and updated status
                node_object.updated_status()

                # append to parent
                self.mapped_classes.append(node_object)

        # if there are already objects mapped to record harmonise by deleting anything not in incoming
        # xml file. This should be skipped for singular and manditory items (like patient) by setting
        # self.sqla_relationship to None.
        sqla_relationship = child_node.sqla_mapped()  # type : ignore
        if sqla_relationship:
            self.add_deleted(sqla_relationship, mapped_ids)

    def add_deleted(self, sqla_mapped: str, mapped_ids: List[str]) -> None:
        # stage records for deletion using the lazy mapping and a list of ids of records in the file
        # this is only needed if the is a one to many relationship between parent and child
        # this function stages for deletion objects which appear mapped but don't appear in incoming file
        # This highlights a problem with the idx method creating keys. What if an item in the middle of the
        # order gets deleted then everything below gets bumped up one.

        mapped_orms = [orm for orm in getattr(self.orm_object, sqla_mapped)]

        self.deleted_orm = self.deleted_orm + [
            record for record in mapped_orms if record.id not in mapped_ids
        ]

    def get_orm_list(
        self, 
        statuses: List[RecordStatus] = [RecordStatus.NEW],
        count_all: bool = True
    ) -> Tuple[Dict[RecordStatus, List], Dict[RecordStatus, int]]:
        """Get ORM objects grouped by status with optional counting.
        
        Args:
            statuses: Statuses to filter by. Defaults to [NEW].
            count_all: Whether to count all statuses. Defaults to True.
        
        Returns:
            Tuple of (objects_by_status, counts_by_status).
            objects_by_status will only contain keys for requested statuses.
        """
        # Initialize results
        orm_objects = {status: [] for status in statuses}
        counts = {RecordStatus.NEW: 0, RecordStatus.MODIFIED: 0, RecordStatus.UNCHANGED: 0}
        
        # Get current record's status
        current_state = self.status
        
        # Add to counts
        counts[current_state] += 1
        
        # Add to objects dict if status matches requested statuses
        if current_state in statuses:
            orm_objects[current_state].append(self.orm_object)
        
        # Process children
        if self.mapped_classes:
            for child_class in self.mapped_classes:
                child_objects, child_counts = child_class.get_orm_list(statuses, count_all)
                
                # Merge child objects for each status
                for status in statuses:
                    if status in child_objects:
                        orm_objects[status].extend(child_objects[status])
                
                # Add child counts
                for s in RecordStatus:
                    counts[s] += child_counts[s]
        
        return orm_objects, counts

    def get_orm_deleted(self) -> list:
        # function to walk through the patient record structure an retrieve
        # records staged for deletion
        if self.mapped_classes:
            orm_objects = self.deleted_orm
            for child_class in self.mapped_classes:
                orm_objects = orm_objects + child_class.get_orm_deleted()
            return orm_objects
        else:
            return self.deleted_orm

    def updated_status(self) -> None:
        # function to update things like dates if object is changed
        # these type of changes should be made carefully to avoid churn
        # should potentially be set in the db in the future
        assert self.orm_object is not None  # nosec
        if self.status == RecordStatus.MODIFIED:
            self.orm_object.update_date = datetime.now()

    def generate_parent_data(self, seq_no: int) -> dict:
        # This function allows attributes to be passed from parent to child
        # Overwrite with whatever is needed to generate the id or whatever
        # of the child record.
        return {"pid": self.pid, "idx": seq_no}

    # In most cases the model for any give xml item can be added by simply
    # overwriting the following two methods
    @classmethod
    @abstractmethod
    def sqla_mapped() -> str:
        # Set to the name of the relationship to the child in the parent sqla
        # model. It is used to delete any records which are not found in the
        # incoming file. If there is always a single child  per parent set to
        # None.
        pass

    @abstractmethod
    def map_xml_to_orm(self, session: Session) -> None:
        # In this function all the idiosyncracies of the xml and the database are hard coded
        pass


class UKRRRefTableBase:
    def __init__(self, renalreg_session: Session, ukrdc_session: Session):
        self.ukrr_session = renalreg_session
        self.ukrdc_session = ukrdc_session
        self.orm_object: sqla.Base

    def backup_to_file(self, filepath: str):
        # query codes
        ukrr_codes_to_sync = (
            self.ukrr_session.execute(select(self.orm_object)).scalars().all()
        )

        # write out codes to file
        with open(filepath, mode="w", newline="") as file:
            writer = csv.writer(file)

            # Write header row
            header = [column.name for column in self.orm_object.__table__.columns]
            writer.writerow(header)

            # Write data rows
            for code in ukrr_codes_to_sync:
                row = [
                    getattr(code, column.name)
                    for column in self.orm_object.__table__.columns
                ]
                writer.writerow(row)

    def sync_table_from_renalreg(self):
        """To start with we just do a full sync but in the future we can add in
        functionality so that only some codes get synced for e.g if new codes
        have been added which aren't in the ukrdc.

        This should have been simply a case of detaching and merging but there
        are issues with copying from one dialect to another so instead we
        manually copy to a blank orm object.
        """

        # query all renalreg records
        ukrr_codes_to_sync = (
            self.ukrr_session.execute(select(self.orm_object)).scalars().all()
        )

        # iterate through records
        for ukrr_code in ukrr_codes_to_sync:
            # we have to  manually copy attributes because they are different
            # dialects of sql
            # Create a dictionary to store the values
            values = {}
            if not ukrr_code:
                # not sure why this is a thing
                print(":)")
                continue

            # only insert values with non null keys
            keys = self.key_properties()
            do_not_insert = False
            for key in keys:
                value = getattr(ukrr_code, key)
                if not value:
                    do_not_insert = True

            if do_not_insert:
                continue

            for column in self.orm_object.__table__.columns:

                name_lower = column.name.lower()
                column_name = self.column_aliases().get(name_lower, name_lower)

                value = getattr(ukrr_code, column_name)
                # sqla doesn't like bit/bool
                if isinstance(value, bool):
                    value = "1" if value else "0"

                values[column_name] = value

            self.ukrdc_session.merge(self.orm_object(**values))

        self.ukrdc_session.commit()

    def column_aliases(self):
        return {}

    @classmethod
    @abstractmethod
    def key_properties():
        """Everything required to uniquely define a record in one of the
        reference tables.
        """
        pass
