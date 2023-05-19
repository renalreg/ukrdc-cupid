from __future__ import annotations
import ukrdc_xsdata.ukrdc as xsd_ukrdc
import ukrdc_xsdata.ukrdc.lab_orders as xsd_lab_orders
import ukrdc_xsdata.ukrdc.types as xsd_types
import ukrdc_sqla.ukrdc as sqla
import ukrdc_cupid.core.store.keygen as key_gen

from abc import ABC, abstractmethod
from typing import Optional


class Node(ABC):
    """
    The xml files and the orm objects have a tree structure. This class is designed
    to abstract all of the idiocyncracies of the xml and the models into a class which allow
    generic methods to be applied to all members of the tree. This allows seperation of the
    logic to map xml to orm objects and the manipulation of those objects.
    """

    def __init__(self, xml, seq_no=None):
        self.xml = xml
        self.mapped_classes = []
        self.extra = None
        self.seq_no = seq_no

    def add_item(self, property, value: str, is_optional=True, is_datetime=False):
        # add properties which constitute a single value
        if is_optional:
            if value:
                if is_datetime:
                    setattr(self.orm_object, property, value.to_datetime())
                else:
                    setattr(self.orm_object, property, value)
        else:
            if is_datetime:
                setattr(self.orm_object, property, value.to_datetime())
            else:
                setattr(self.orm_object, property, value)

    def add_children(self, child_node: Node, xml_items: xsd_ukrdc, single=False):
        # add child nodes to the tree
        if single:
            node = child_node(xml_items)
            node.map_xml_to_tree()
            self.mapped_classes.append(node)

        else:
            for xml_item in xml_items:
                node = child_node(xml_item)
                node.map_xml_to_tree()
                self.mapped_classes.append(node)

    def add_code(property_code, property_description, property_std, xml_code: xsd_types.CodedField, optional=True):
        # add properties which are coded fields
        if optional is True:
            if xml_code:
                print("append_code")
        else:
            print("append code")

    def transform(self, pid: str):
        """
        Abstraction to propagate transformation down through dependent classes
        """
        self.transformer(pid=pid)
        for child_class in self.mapped_classes:
            child_class.transformer(pid)

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
        self.orm_object = sqla.ResultItem()
        super().__init__(xml, seq_no)

    def map_xml_to_tree(self):
        print("ting")

    def transformer(self, order_id: str, seq_no: int):
        self.orm_object.id = key_gen.generate_key_resultitem(self.orm_object, order_id=order_id, seq_no=seq_no)


class LabOrder(Node):
    def __init__(self, xml: xsd_lab_orders.LabOrder, seq_no: int = None):
        self.orm_object = sqla.LabOrder()
        super().__init__(xml, seq_no)

    def map_xml_to_tree(self):
        self.add_item("placerid", self.xml.placer_id)
        self.add_item("fillerid", self.xml.filler_id)
        self.add_item("specimencollectedtime", self.xml.specimen_collected_time)
        self.add_item("specimenreceivedtime", self.xml.specimen_received_time)
        self.add_item("specimensource", self.xml.specimen_source)

    def transform(self, pid):
        self.transformer(pid)
        for child_class in self.mapped_classes:
            child_class.transformer(child_class.orm_object, order_id=self.orm_object.order_id, seq_no=child_class.seq_no)

    def transformer(self, pid):
        # we overwrite the base class because we result item needs extra info
        self.orm_object.pid = pid
        id = key_gen.generate_key_laborder(self.orm_object, pid)
        self.orm_object.id = id
        return

    def assemble_orm_tree(self):
        for mapped_class in self.mapped_classes:
            self.orm_object.result_items = [mapped_class.orm_object]
        return self.orm_object


class Patient(Node):
    """Initialise node for the patient object"""

    def __init__(self, xml: xsd_ukrdc.Patient, seq_no: int = None):
        self.orm_object = sqla.Patient()
        super().__init__(xml, seq_no)

    def map_xml_to_tree(self):
        self.add_item("birthtime", self.xml.birth_time.to_datetime())
        self.add_item("deathtime", self.xml.death_time)
        self.add_item("gender", self.xml.gender)
        self.add_item("countryofbirth", self.xml.country_of_birth)

    def transformer(self, pid: str):
        self.orm_object.pid = pid

    def assemble_orm_tree(self):
        for mapped_class in self.mapped_classes:
            mapped_class.assemble_orm_tree()
        return self.orm_object


class PatientRecord(Node):
    def __init__(self, xml: xsd_ukrdc.PatientRecord, seq_no: int = None):
        self.orm_object = sqla.PatientRecord()
        super().__init__(xml, seq_no)

    def map_xml_to_tree(self):
        self.add_item("sendingfacility", self.xml.sending_facility.value)
        self.add_item("sendingextract", self.xml.sending_extract.value)
        self.add_children(Patient, self.xml.patient, single=True)
        self.add_children(LabOrder, self.xml.lab_orders.lab_order)

    def transformer(self, pid: str):
        self.orm_object.pid = pid

    def assemble_orm_tree(self):
        # Assembles the sqla objects back into thier hierarchy.
        # assuming the foreign keys have been set up properly this shouldn't
        # strictly be nessary
        for mapped_class in self.mapped_classes:
            orm_object = mapped_class.assemble_orm_tree()

            if isinstance(orm_object, sqla.Patient):
                self.orm_object.patient = orm_object
            if isinstance(orm_object, sqla.LabOrder):
                if self.orm_object.lab_orders:
                    self.orm_object.lab_orders.append(orm_object)
                else:
                    self.orm_object.lab_orders = [orm_object]

        return self.orm_object
