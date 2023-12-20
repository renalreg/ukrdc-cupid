from __future__ import annotations  # allows typehint of node class

from ukrdc_cupid.core.store.models.structure import Node
from ukrdc_cupid.core.store.models.patient import Patient
from ukrdc_cupid.core.store.models.child_records import Observation, LabOrder

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from sqlalchemy import and_

from typing import List, Type

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

    def sqla_mapped() -> None:
        return None

    def add_children(self, child_node: type[Node], xml_attr: str, session: Session) -> None:
        
        super().add_children(child_node, xml_attr, session) 

    def updated_status(self) -> None:
        super().updated_status()
        if self.is_new_record:
            self.orm_object.repositorycreationdate = self.repository_updated_date

        if self.is_modified or self.is_new_record:
            # what is the correct behaviour should this be set if any part of the patient record has been changed?
            # I think this should be a nullable field
            self.orm_object.repositoryupdatedate = self.repository_updated_date

    def map_xml_to_orm(self, session: Session) -> None:

        # core patient record
        self.add_item("sendingfacility", self.xml.sending_facility)
        self.add_item("sendingextract", self.xml.sending_extract)

        # get MRN from patient numbers model
        for number in self.xml.patient.patient_numbers[0].patient_number:
            if number.number_type.value == "MRN":
                self.orm_object.localpatientid = number.number

        self.add_children(Patient, "patient", session)
        self.add_children(Observation, "observations.observation", session)
        self.add_children(LabOrder, "lab_orders.lab_order", session)

    def map_to_database(
        self, pid: str, ukrdcid: str, session: Session, is_new=True
    ) -> None:
        self.pid = pid
        self.session = session
        self.is_new_record = is_new

        # load or create the orm
        if is_new:
            self.orm_object = self.orm_model(pid=self.pid, ukrdcid=ukrdcid)
        else:
            self.orm_object = session.get(self.orm_model, self.pid)

        self.map_xml_to_orm(session)
        self.updated_status()

    def add_deleted(self, sqla_mapped: str, mapped_ids: List[str]) -> None:
        # we only delete within a time window for observations and lab orders
        if sqla_mapped == "observations":
            mapped_orms = self.session.query(sqla.Observation)
        
        elif sqla_mapped == "laborders":
            mapped_orms = self.session.query(sqla.LabOrder).filter(and_(sqla.LabOrder.specimen_collected_time >=self.lab_order_range[0], sqla.LabOrder.specimen_collected_time <= self.lab_order_range[1]))
        else:
            mapped_orms = getattr(self.orm_object, sqla_mapped)
            
        self.deleted_orm = [
            record for record in mapped_orms if record.id not in mapped_ids
        ]
