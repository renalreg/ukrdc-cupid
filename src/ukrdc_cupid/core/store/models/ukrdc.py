from __future__ import annotations  # allows typehint of node class

from ukrdc_cupid.core.store.models.structure import Node
from ukrdc_cupid.core.store.models.patient import Patient
from ukrdc_cupid.core.store.models.child_records import Observation

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session


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

    def updated_status(self, session: Session) -> None:
        super().updated_status(session)
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
        self.add_children(Observation, "observations.observation", session, True)

        self.updated_status(session)

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
