"""
Models to create sqla objects from an xml file 
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ukrdc_cupid.core.store.models.structure import Node
import ukrdc_cupid.core.store.keygen as key_gen  # type: ignore
import ukrdc_sqla.ukrdc as sqla
import ukrdc_xsdata.ukrdc.observations as xsd_observations  # type: ignore
import ukrdc_xsdata.ukrdc.lab_orders as xsd_lab_orders  # type: ignore


class Observation(Node):
    def __init__(self, xml: xsd_observations.Observation):
        super().__init__(xml, sqla.Observation)

    def sqla_mapped() -> str:
        return "observations"

    def map_xml_to_orm(self, _) -> None:

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


class ResultItem(Node):
    def __init__(self, xml: xsd_lab_orders.ResultItem):
        super().__init__(xml, sqla.ResultItem)

    def sqla_mapped() -> str:
        return "result_items"

    def map_xml_to_orm(self, _):
        # fmt: off
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
        # fmt: on


class LabOrder(Node):
    def __init__(self, xml: xsd_lab_orders.LabOrder):
        super().__init__(xml, sqla.LabOrder)

    def sqla_mapped() -> str:
        return "lab_orders"

    def generate_id(self, _) -> str:
        return key_gen.generate_key_laborder(self.xml, self.pid)

    def generate_parent_data(self, seq_no: int):
        return {"idx": seq_no, "order_id": self.orm_object.id}

    def map_xml_to_orm(self, session: Session) -> None:
        # fmt: off
        self.add_item("placerid", self.xml.placer_id, optional=False)
        self.add_item("fillerid", self.xml.filler_id, optional=True)
        self.add_item("specimencollectedtime", self.xml.specimen_collected_time, optional=True)
        self.add_item("status", self.xml.status, optional=True)
        self.add_item("specimenreceivedtime", self.xml.specimen_received_time, optional=True)

        self.add_item("specimensource", self.xml.specimen_source, optional=True)
        self.add_item("duration", self.xml.duration, optional=True)
        self.add_item("enteredon", self.xml.entered_on, optional=True)
        self.add_item("updatedon", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)

        self.add_code("receivinglocationcode","receivinglocationcodestd","receivinglocationdesc",self.xml.receiving_location,optional=True)
        self.add_code("orderedbycode","orderedbycodestd","orderedbydesc",self.xml.ordered_by,optional=True)
        self.add_code("orderitemcode","orderitemcodestd","orderitemdesc",self.xml.order_item,optional=True)
        self.add_code("ordercategorycode","ordercategorycodestd","ordercategorydesc",self.xml.order_category,optional=True)
        self.add_code("prioritycode","prioritycodestd","prioritydesc",self.xml.priority,optional=True)
        # self.add_patient_class(self.xml.patient_class)
        self.add_code("patientclasscode", "patientclassdesc", "patientclasscodestd", self.xml.patient_class, optional=True)
        self.add_code("enteredatcode","enteredatdesc","enteredatcodestd",self.xml.entered_at,optional=True)
        self.add_code("enteringorganizationcode","enteringorganizationcodestd","enteringorganizationdesc",self.xml.entering_organization,optional=True)
        
        self.add_children(ResultItem, "result_items.result_item", session)
        # fmt: on
