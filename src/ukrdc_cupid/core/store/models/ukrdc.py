"""
These models contain the orm specific bits of deserialising/converting the xml 
to orm. Currently they try and strike a balance between code that is to verbose
and boilerplatey and code which is complicated/implicit. 

In the future this would benefit from a separate set of ukrdc deserialisation 
models which:

1) Creates boilerplate for the models programatically/intellegently this might 
require making liberal use of the sqla synonym properties
2) Bin off xsdata and pyxb tortoises. Would be better to convert from the xml
to orm.  
3) Can take either lxml or or orm as an input
4) Contain to_xml() and to_orm() methods and unify functionality with repos
5) Contain the relationship between the primary keys and the order of items
this could include a sort by date or something. 

These would save a considerable amount of effort in the different places where
we are doing this kind of thing. 
"""

from __future__ import annotations  # allows typehint of node class

from typing import Union
from ukrdc_cupid.core.store.models.utils import cull_singlet_lists
from ukrdc_cupid.core.store.models.structure import Node
from ukrdc_cupid.core.store.models.patient import (
    Patient,
    SocialHistory,
    FamilyHistory,
    Allergy,
    Diagnosis,
    RenalDiagnosis,
    CauseOfDeath,
    Document,
    Survey,
)
from ukrdc_cupid.core.store.models.longitudinal_records import (
    Observation,
    Procedure,
    Transplant,
    LabOrder,
    DialysisSession,
    Treatment,
    VascularAccess,
    Medication,
    TransplantList,
    Encounter,
)
from ukrdc_cupid.core.store.models.relationships import (
    ClinicalRelationship,
    OptOut,
    ProgramMembership,
)

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
import ukrdc_xsdata.ukrdc.lab_orders as xsd_lab_orders
import ukrdc_xsdata.ukrdc.observations as xsd_observations
import ukrdc_xsdata.ukrdc.dialysis_sessions as xsd_dialysis_sessions
import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from sqlalchemy import and_
import datetime as dt

from typing import List


def set_start_stop(
    xml: Union[xsd_lab_orders, xsd_observations, xsd_dialysis_sessions], property: str
):
    items = cull_singlet_lists(getattr(xml, property))

    if items:
        # if start and stop are not present we interpret them as all time up to now
        if items.start:
            start = items.start.to_datetime()
        else:
            start = dt.datetime(1899, 9, 9)

        if items.stop:
            stop = items.stop.to_datetime()
        else:
            stop = dt.datetime.now()

        return [start, stop]

    return None


class PatientRecord(Node):
    def __init__(self, xml: xsd_ukrdc.PatientRecord):
        super().__init__(xml, sqla.PatientRecord)

        # some records have an additional date (aside from the usual ones update by db triggers)
        # we will now use this to host the date that gets sent on the sending facility
        self.repository_updated_date = xml.sending_facility.time.to_datetime()
        self.lab_order_range = set_start_stop(xml, "lab_orders")
        self.observation_range = set_start_stop(xml, "observations")

        self.dialysis_session_range = None
        if xml.procedures:
            self.dialysis_session_range = set_start_stop(
                xml.procedures, "dialysis_sessions"
            )

    def sqla_mapped() -> None:
        return None

    def add_sending_facility(self):
        """Parse sendingfacility"""
        sending_facility = self.xml.sending_facility
        self.orm_object.sendingfacility = sending_facility.value
        self.orm_object.channelname = sending_facility.channel_name
        self.orm_object.schemaversion = sending_facility.schema_version
        # self.orm_object.

    def updated_status(self) -> None:
        super().updated_status()
        if self.is_new_record:
            self.orm_object.repositorycreationdate = (
                self.repository_updated_date
            )  # type:ignore

        if self.is_modified or self.is_new_record:
            # what is the correct behaviour should this be set if any part of the patient record has been changed?
            # I think this should be a nullable field
            self.orm_object.repositoryupdatedate = (
                self.repository_updated_date
            )  # type:ignore

    def map_xml_to_orm(self, session: Session) -> None:

        # metadata for patientfeed
        self.add_item("sendingextract", self.xml.sending_extract)
        self.add_sending_facility()

        # get MRN from patient numbers model
        for number in self.xml.patient.patient_numbers.patient_number:
            if number.number_type.value == "MRN":
                self.orm_object.localpatientid = number.number  # type :ignore

        # fmt: off
        self.add_children(Patient, "patient", session)
        self.add_children(SocialHistory, "social_histories.social_history", session)
        self.add_children(FamilyHistory, "family_histories.family_history", session)
        self.add_children(Allergy, "allergies.allergy", session)
        self.add_children(Medication, "medications.medication", session)

        self.add_children(Diagnosis, "diagnoses.diagnosis", session)
        self.add_children(RenalDiagnosis, "diagnoses.renal_diagnosis", session)
        self.add_children(CauseOfDeath, "diagnoses.cause_of_death", session)
        self.add_children(Observation, "observations.observation", session)
        self.add_children(LabOrder, "lab_orders.lab_order", session)
        self.add_children(Procedure, "procedures.procedure", session)

        self.add_children(DialysisSession, "procedures.dialysis_sessions.dialysis_session", session)
        self.add_children(VascularAccess, "procedures.vascular_access", session)
        self.add_children(Transplant, "procedures.transplant", session)
        self.add_children(Treatment, "encounters.treatment", session)
        self.add_children(ProgramMembership, "program_memberships.program_membership", session)
        self.add_children(OptOut, "opt_outs.opt_out", session)
        self.add_children(ClinicalRelationship, "clinical_relationships.clinical_relationship", session)

        self.add_children(Document, "documents.document", session)
        self.add_children(Encounter, "encounters.encounter", session)
        self.add_children(TransplantList,"encounters.transplant_list", session)
        self.add_children(Survey, "surveys.survey", session)
        # fmt: on

    def map_to_database(
        self, pid: str, ukrdcid: str, session: Session, is_new=True
    ) -> None:
        self.pid = pid
        self.session = session
        self.is_new_record = is_new

        # load or create the orm
        if is_new:
            self.orm_object = self.orm_model(
                pid=self.pid, ukrdcid=ukrdcid
            )  # type:ignore
        else:
            self.orm_object = session.get(self.orm_model, self.pid)

        self.map_xml_to_orm(session)
        self.updated_status()

    def add_deleted(self, sqla_mapped: str, mapped_ids: List[str]) -> None:
        # we only delete within a time window for observations and lab orders
        # don't like this solution very much. Think may sqla needs to become
        # a function which returns the mapped_orms.
        if sqla_mapped == "observations":
            if self.observation_range is not None:
                mapped_orms = (
                    self.session.query(sqla.Observation)
                    .filter(
                        and_(
                            sqla.Observation.observation_time
                            >= self.observation_range[0],
                            sqla.Observation.observation_time
                            <= self.observation_range[1],
                        )
                    )
                    .all()
                )
            else:
                mapped_orms = []

        elif sqla_mapped == "lab_orders":
            if self.lab_order_range is not None:
                mapped_orms = (
                    self.session.query(sqla.LabOrder)
                    .filter(
                        and_(
                            sqla.LabOrder.specimen_collected_time
                            >= self.lab_order_range[0],
                            sqla.LabOrder.specimen_collected_time
                            <= self.lab_order_range[1],
                        )
                    )
                    .all()
                )
            else:
                mapped_orms = []

        elif sqla_mapped == "dialysis_sessions":
            if self.dialysis_session_range is not None:
                mapped_orms = (
                    self.session.query(sqla.DialysisSession)
                    .filter(
                        and_(
                            sqla.DialysisSession.proceduretime
                            >= self.dialysis_session_range[0],
                            sqla.DialysisSession.proceduretime
                            <= self.dialysis_session_range[1],
                        )
                    )
                    .all()
                )
            else:
                mapped_orms = []
        else:
            # In most cases we can just use the lazy mapping from the sqla models
            mapped_orms = getattr(self.orm_object, sqla_mapped)

        # stage records for deletion
        for record in mapped_orms:
            if record.id not in mapped_ids:
                self.deleted_orm.append(record)
                # we need to nuke result items too
                if sqla_mapped == "lab_orders":
                    for result_item in record.result_items:
                        self.deleted_orm.append(result_item)

    def generate_parent_data(self, seq_no: int):
        parent_data = super().generate_parent_data(seq_no=seq_no)
        parent_data["repositoryupdatedate"] = self.repository_updated_date
        return parent_data
