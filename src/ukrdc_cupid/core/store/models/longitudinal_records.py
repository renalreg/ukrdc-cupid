"""
These models store longitudinal records (where time or perhaps entropy is a key
variable). 

Some of these occur with such regularity that they are not included in full in
each xml file which is sent. These are windowed in time which creates a few 
different modes of insertion depending on whether or not we delete the records 
missing in the xml file in the window.  
"""

from __future__ import annotations
from sqlalchemy.orm import Session

import ukrdc_sqla.ukrdc as sqla
from ukrdc_cupid.core.store.models.structure import Node, RecordStatus
import ukrdc_cupid.core.store.keygen as key_gen  # type: ignore

import ukrdc_xsdata.ukrdc.observations as xsd_observations  # type: ignore
import ukrdc_xsdata.ukrdc.lab_orders as xsd_lab_orders  # type: ignore
import ukrdc_xsdata.ukrdc.dialysis_sessions as xsd_dialysis_sessions  # type: ignore
import ukrdc_xsdata.ukrdc.procedures as xsd_procedures
import ukrdc_xsdata.ukrdc.vascular_accesses as xsd_vascular_accesses
import ukrdc_xsdata.ukrdc.encounters as xsd_encounters  # type: ignore
import ukrdc_xsdata.ukrdc.transplants as xsd_transplants  # type: ignore


class Observation(Node):
    def __init__(self, xml: xsd_observations.Observation):
        super().__init__(xml, sqla.Observation)

    def sqla_mapped() -> str:
        return "observations"

    def generate_id(self, seq_no: int) -> str:
        seq_no = 0  # hardcode as zero to prevent problems with ex-missing
        return key_gen.generate_key_observations(self.xml, self.pid, seq_no)

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

    def generate_id(self, seq_no: str, order_id: str) -> str:
        # define id generation method for consistency
        return key_gen.generate_key_resultitem(self.xml, order_id, seq_no)

    def map_to_database(self, session: Session, seq_no: int, order_id: str) -> str:
        # look up key in database and make new orm if it doesn't exist
        id = self.generate_id(seq_no, order_id)
        self.orm_object = session.get(self.orm_model, id)

        if self.orm_object is None:
            self.orm_object = self.orm_model(id=id)  # type:ignore
            self.status = RecordStatus.NEW

        else:
            self.is_new_record = False

        return id

    def map_xml_to_orm(self):

        # fmt: off
        self.add_item("resulttype", self.xml.result_type)
        self.add_code("serviceidcode", "serviceidcodestd", "serviceiddesc", self.xml.service_id)
        self.add_item("subid", self.xml.sub_id)
        self.add_item("resultvalue", self.xml.result_value)
        self.add_item("resultvalueunits", self.xml.result_value_units)
        self.add_item("referencerange", self.xml.reference_range)
        self.add_item("interpretationcodes", self.xml.interpretation_codes)
        self.add_item("prepost", self.xml.pre_post)
        self.add_item("enteredon", self.xml.entered_on)
        self.add_item("status", self.xml.status)
        self.add_item("observationtime", self.xml.observation_time)
        self.add_item("commenttext", self.xml.comments)
        self.add_item("referencecomment", self.xml.reference_comment)
        # fmt: on


class LabOrder(Node):
    def __init__(self, xml: xsd_lab_orders.LabOrder):
        super().__init__(xml, sqla.LabOrder)
        # we will need this for generating resultitem keys
        self.parent_data: dict = None

    def sqla_mapped() -> str:
        return "lab_orders"

    def generate_id(self, _) -> str:
        return key_gen.generate_key_laborder(self.xml, self.pid)

    def add_children(self, session: Session) -> None:

        # unpack the xml_items:
        if self.xml.result_items:
            result_items = self.xml.result_items.result_item

        result_item_ids = []
        for seq_no, result_item in enumerate(result_items):
            # initialize result item
            order_id = self.orm_object.id
            result_obj = ResultItem(xml=result_item)

            # map to database
            id = result_obj.map_to_database(session, seq_no, order_id)
            result_item_ids.append(id)

            # Map the rest of the fields
            result_obj.map_xml_to_orm()
            result_obj.orm_object.order_id = order_id
            result_obj.updated_status()

            # append to parent
            self.mapped_classes.append(result_obj)

        self.add_deleted(ResultItem.sqla_mapped(), result_item_ids)

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
        
        self.add_children(session)
        # fmt: on


class DialysisSession(Node):
    def __init__(self, xml: xsd_dialysis_sessions.DialysisSession):
        super().__init__(xml, sqla.DialysisSession)

    def sqla_mapped() -> str:
        return "dialysis_sessions"

    def generate_id(self, _) -> str:
        # See UC-50: This is caused by enumerating the dialysis sessions which
        # prevents them correctly linked to the right records because of the
        # idx enumerator
        return key_gen.generate_key_dialysis_session(self.xml, self.pid)

    def map_xml_to_orm(self, _) -> None:
        # fmt: off
        # codes
        self.add_code("enteredatcode", "enteredatcodestd", "enteredatdesc", self.xml.entered_at)
        self.add_code("enteredbycode", "enteredbycodestd", "enteredbydesc", self.xml.entered_at)
        self.add_code("proceduretypecode", "proceduretypecodestd", "proceduretypedesc", self.xml.procedure_type)
        
        # times
        self.add_item("proceduretime", self.xml.procedure_time)
        self.add_item("updatedon", self.xml.updated_on)

        # ids
        self.add_item("externalid", self.xml.external_id)
        
        # values
        self.add_item("qhd19", self.xml.symtomatic_hypotension)
        if self.xml.vascular_access:
            self.add_item("qhd20", self.xml.vascular_access.code)
        if self.xml.vascular_access_site:
            self.add_item("qhd21", self.xml.vascular_access_site.code)
        self.add_item("qhd31", self.xml.time_dialysed)
        # fmt: on


class Procedure(Node):
    def __init__(self, xml: xsd_procedures.Procedure):
        super().__init__(xml, sqla.Procedure)

    def sqla_mapped() -> str:
        return "procedures"

    def map_xml_to_orm(self, _) -> None:
        # fmt: off
        pass
        # fmt: on


class VascularAccess(Node):
    def __init__(self, xml: xsd_vascular_accesses.VascularAccess):
        super().__init__(xml, sqla.VascularAccess)

    def sqla_mapped() -> str:
        return "vascular_accesses"

    # fmt: off
    def add_acc(self):
        if self.xml.attributes:
            self.add_item("acc19", self.xml.attributes.acc19)
            self.add_item("acc20", self.xml.attributes.acc20)
            self.add_item("acc21", self.xml.attributes.acc21)
            self.add_item("acc22", self.xml.attributes.acc22)
            self.add_item("acc30", self.xml.attributes.acc30)
            self.add_item("acc40", self.xml.attributes.acc40)

    def map_xml_to_orm(self, _) -> None:
        # Map values from XML to ORM object
        self.add_code("proceduretypecode", "proceduretypecodestd", "proceduretypedesc",self.xml.procedure_type,optional=False,)
        self.add_item("proceduretime", self.xml.procedure_time, optional=False)
        #self.add_code("enteredbycode", "enteredbycodestd", "enteredbydesc", self.xml.entered_by, optional=True,)
        self.add_code("enteredatcode", "enteredatcodestd", "enteredatdesc", self.xml.entered_at, optional=True,)
        self.add_item("updatedon", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)
        self.add_acc()
        # fmt: on
        pass


class Transplant(Node):
    def __init__(self, xml: xsd_transplants.TransplantProcedure):
        super().__init__(xml, sqla.Transplant)

    def sqla_mapped() -> str:
        return "transplants"

    def map_xml_to_orm(self, _) -> None:
        # fmt: off
        self.add_code("proceduretypecode", "proceduretypecodestd", "proceduretypedesc", self.xml.procedure_type, optional=False)
        self.add_item("proceduretime", self.xml.procedure_time, optional=False)
        self.add_code("enteredatcode", "enteredatcodestd", "enteredatdesc", self.xml.entered_at)

        self.add_item("updatedon", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)

        # former attributes
        self.add_item("tra77", self.xml.donor_type)
        # this may need adding to the sqla models
        #self.add_item("tra72", self.xml.date_registered)
        self.add_item("tra64", self.xml.failure_date)
        self.add_item("tra91", self.xml.cold_ischaemic_time)
        self.add_item("tra83", self.xml.hlamismatch_a)
        self.add_item("tra84", self.xml.hlamismatch_b)
        self.add_item("tra85", self.xml.hlamismatch_c)
        # fmt: on


class Treatment(Node):
    def __init__(self, xml: xsd_encounters.Treatment):
        super().__init__(xml, sqla.Treatment)

    def sqla_mapped() -> str:
        return "treatments"

    def map_xml_to_orm(self, _) -> None:
        # fmt: off
        self.add_item("encounternumber", self.xml.encounter_number, optional=True)
        self.add_item("fromtime", self.xml.from_time, optional=False)
        self.add_item("totime", self.xml.to_time, optional=True)
        self.add_code("admittingcliniciancode", "admittingcliniciancodestd", "admittingcliniciandesc", self.xml.admitting_clinician, optional=True)
        self.add_code("healthcarefacilitycode", "healthcarefacilitycodestd", "healthcarefacilitydesc", self.xml.health_care_facility, optional=True)
        self.add_code( "admitreasoncode", "admitreasoncodestd", "admitreasondesc", self.xml.admit_reason, optional=True)
        self.add_code("admissionsourcecode", "admissionsourcecodestd", "admissionsourcedesc", self.xml.admission_source,optional=True)
        self.add_code("dischargereasoncode", "dischargereasoncodestd","dischargereasondesc",self.xml.discharge_reason,optional=True,)
        self.add_code("dischargelocationcode","dischargelocationcodestd","dischargelocationdesc",self.xml.discharge_location,optional=True,)
        self.add_code("enteredatcode","enteredatcodestd","enteredatdesc",self.xml.entered_at,optional=True)

        self.add_item("visitdescription", self.xml.visit_description, optional=True)
        
        if self.xml.attributes:
            self.add_item("qbl05", self.xml.attributes.qbl05, optional=True)

        # common metadata
        self.add_item("update_date", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)
        # fmt: on


class Medication(Node):
    def __init__(self, xml):
        super().__init__(xml, sqla.Medication)

    def sqla_mapped():
        return "medications"

    def add_drug_product(self):
        # fmt: off
        self.add_code("drugproductidcode", "drugproductidcodestd", "drugproductiddesc", self.xml.drug_product.id)
        self.add_item("drugproductgeneric", self.xml.drug_product.generic)
        self.add_item("drugproductlabelname", self.xml.drug_product.label_name)
        self.add_code("drugproductformcode", "drugproductformcodestd", "drugproductformdesc", self.xml.drug_product.form)
        self.add_code("drugproductstrengthunitscode", "drugproductstrengthunitscodestd", "drugproductstrengthunitsdesc", self.xml.drug_product.strength_units)
        # fmt: on

    def map_xml_to_orm(self, _):
        # fmt: off
        self.add_item("prescriptionnumber", self.xml.prescription_number)
        self.add_item("fromtime", self.xml.from_time)
        self.add_item("totime", self.xml.to_time)
        self.add_code("enteringorganizationcode", "enteringorganizationcodestd", "enteringorganizationdesc", self.xml.entering_organization)
        self.add_code( "routecode", "routecodestd", "routedesc", self.xml.route)
        if self.xml.drug_product:
            self.add_drug_product()
        
        self.add_item("frequency", self.xml.frequency)
        self.add_item("commenttext", self.xml.comments)
        self.add_item("dosequantity", self.xml.dose_quantity)
        self.add_code("doseuomcode", "doseuomcodestd", "doseuomdesc",self.xml.dose_uo_m)
        self.add_item("indication", self.xml.indication)
        self.add_item("encounternumber", self.xml.encounter_number)
        self.add_item("updatedon", self.xml.updated_on)
        self.add_item("externalid", self.xml.external_id)
        # fmt: on


class TransplantList(Node):
    def __init__(self, xml: xsd_encounters.TransplantList):
        super().__init__(xml, sqla.TransplantList)

    def sqla_mapped():
        return "transplantlists"

    def map_xml_to_orm(self, _):
        # fmt: off
        self.add_item("encounternumber", self.xml.encounter_number, optional=False)
        self.add_item("encountertype", self.xml.encounter_type, optional=True)
        self.add_item("fromtime", self.xml.from_time, optional=False)
        self.add_item("totime", self.xml.to_time, optional=True)
        self.add_code("admittingcliniciancode", "admittingcliniciancodestd", "admittingcliniciandesc", self.xml.admitting_clinician, optional=True)
        self.add_code("healthcarefacilitycode", "healthcarefacilitycodestd", "healthcarefacilitydesc", self.xml.health_care_facility, optional=True,)
        self.add_code("admitreasoncode", "admitreasoncodestd", "admitreasondesc", self.xml.admit_reason, optional=True,)
        self.add_code("admissionsourcecode", "admissionsourcecodestd", "admissionsourcedesc", self.xml.admission_source, optional=True)
        self.add_code("dischargereasoncode", "dischargereasoncodestd", "dischargereasondesc", self.xml.discharge_reason, optional=True,)
        self.add_code("dischargelocationcode", "dischargelocationcodestd", "dischargelocationdesc", self.xml.discharge_location, optional=True,)
        self.add_code("enteredatcode", "enteredatcodestd", "enteredatdesc", self.xml.entered_at, optional=True,)
        self.add_item("visitdescription", self.xml.visit_description, optional=True)
        self.add_item("updatedon", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)
        # fmt: on


class Encounter(Node):
    def __init__(self, xml: xsd_encounters.Encounter):
        super().__init__(xml, sqla.Encounter)

    def sqla_mapped():
        return "encounters"

    def map_xml_to_orm(self, _):
        self.add_item("encounternumber", self.xml.encounter_number, optional=True)
        self.add_item("encountertype", self.xml.encounter_type, optional=False)
        self.add_item("fromtime", self.xml.from_time, optional=False)
        self.add_item("totime", self.xml.to_time, optional=True)
        self.add_code(
            "admittingcliniciancode",
            "admittingcliniciancodestd",
            "admittingcliniciandesc",
            self.xml.admitting_clinician,
            optional=True,
        )
        self.add_code(
            "healthcarefacilitycode",
            "healthcarefacilitycodestd",
            "healthcarefacilitydesc",
            self.xml.health_care_facility,
            optional=True,
        )
        self.add_code(
            "admitreasoncode",
            "admitreasoncodestd",
            "admitreasondesc",
            self.xml.admit_reason,
            optional=True,
        )
        self.add_code(
            "admissionsourcecode",
            "admissionsourcecodestd",
            "admissionsourcedesc",
            self.xml.admission_source,
            optional=True,
        )
        self.add_code(
            "dischargereasoncode",
            "dischargereasoncodestd",
            "dischargereasondesc",
            self.xml.discharge_reason,
            optional=True,
        )
        self.add_code(
            "dischargelocationcode",
            "dischargelocationcodestd",
            "dischargelocationdesc",
            self.xml.discharge_location,
            optional=True,
        )
        self.add_code(
            "enteredatcode",
            "enteredatcodestd",
            "enteredatdesc",
            self.xml.entered_at,
            optional=True,
        )
        self.add_item("visitdescription", self.xml.visit_description, optional=True)
        self.add_item("updatedon", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)

        return
