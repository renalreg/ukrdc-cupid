"""
Models to create sqla objects from an xml file 
"""

from __future__ import annotations  # allows typehint of node class

from ukrdc_cupid.core.store.models.structure import Node
import ukrdc_sqla.ukrdc as sqla
import ukrdc_xsdata.ukrdc.observations as xsd_observations  # type: ignore


class Observation(Node):
    def __init__(self, xml: xsd_observations.Observation, seq_no: int):
        super().__init__(xml, sqla.Observation, seq_no)

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
