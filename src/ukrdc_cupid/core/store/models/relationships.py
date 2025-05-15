from ukrdc_cupid.core.store.models.structure import Node
import ukrdc_sqla.ukrdc as sqla
import ukrdc_xsdata.ukrdc.program_memberships as xsd_program_memberships  # type: ignore
import ukrdc_xsdata.ukrdc.opt_outs as xsd_opt_outs  # type: ignore
import ukrdc_xsdata.ukrdc.clinical_relationships as xsd_clinical_relationships  # type: ignore


class ProgramMembership(Node):
    def __init__(self, xml: xsd_program_memberships.ProgramMembership):
        super().__init__(xml, sqla.ProgramMembership)

    def sqla_mapped() -> str:
        return "program_memberships"

    def map_xml_to_orm(self, _):
        # fmt: off
        self.add_code("enteredbycode", "enteredbycodestd","enteredbydesc",self.xml.entered_by)
        self.add_code("enteredatcode", "enteredatcodestd", "enteredatdesc", self.xml.entered_at)
        self.add_item("programname", self.xml.program_name, optional=True)
        self.add_item("programdescription", self.xml.program_description, optional=True)
        self.add_item("fromtime", self.xml.from_time, optional=False)
        self.add_item("totime", self.xml.to_time, optional=True)
        self.add_item("updatedon", self.xml.updated_on, optional=True)
        self.add_item("externalid", self.xml.external_id, optional=True)
        # fmt: on


class OptOut(Node):
    def __init__(self, xml: xsd_opt_outs.OptOut):
        super().__init__(xml, sqla.OptOut)

    def sqla_mapped() -> str:
        return "opt_outs"

    def map_xml_to_orm(self, _):
        # fmt: off
        self.add_item("program_name", self.xml.program_name)
        self.add_item("program_description", self.xml.program_description)
        self.add_code("entered_by_code", "entered_by_code_std", "entered_by_desc", self.xml.entered_by)
        self.add_code("entered_at_code", "entered_at_code_std", "entered_at_desc", self.xml.entered_at)
        self.add_item("from_time", self.xml.from_time, optional=False)
        self.add_item("to_time", self.xml.to_time, optional=True)
        self.add_item("updated_on", self.xml.updated_on, optional=True)
        self.add_item("external_id", self.xml.external_id, optional=True)
        # fmt: on


class ClinicalRelationship(Node):
    def __init__(self, xml: xsd_clinical_relationships.ClinicalRelationship):
        super().__init__(xml, sqla.ClinicalRelationship)

    def sqla_mapped() -> str:
        return "clinical_relationships"

    def map_xml_to_tree(self):
        # fmt: off
        self.add_code("cliniciancode", "cliniciancodestd", "cliniciandesc", self.xml.clinician)
        self.add_code("facilitycode","facilitycodestd","facilitydesc",self.xml.facility_code)
        self.add_item("fromtime", self.xml.from_time, optional=False)
        self.add_item("totime", self.xml.to_time, optional=True)
        self.add_item("updatedon", self.xml.updated_on)
        self.add_item("externalid", self.xml.external_id)
        # fmt: on
