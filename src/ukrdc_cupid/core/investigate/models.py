from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    MetaData,
    Column,
    Integer,
    Boolean,
    String,
    DateTime,
    Text,
    ForeignKey,
    Table,
    text,
)


metadata = MetaData()
Base = declarative_base(metadata=metadata)

GLOBAL_LAZY = "dynamic"

# Many to many relationship exists between pateint ids
# (internal such as ukrdc and external such as NHS)
# this table allows a issue_id to allow multiple patientids to be appended to any particular issue
# similarly it makes it easy to look up which issues are already accosiated with a particular id.

association_table = Table(
    "patientidtoissue",
    Base.metadata,  # type:ignore
    Column("patient_id_id", Integer, ForeignKey("patientid.id")),
    Column("issue_id", Integer, ForeignKey("issue.id")),
)

class PatientID(Base):  # type:ignore
    __tablename__ = "patientid"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(String(50), index=True, nullable=True)
    ukrdcid = Column(String(50), index=True)


class Issue(Base):  # type:ignore
    __tablename__ = "issue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey("issuetype.id"))

    date_created = Column(DateTime, nullable=False)
    error_message = Column(String(100))
    filename = Column(String(100))
    xml_file = Column(Text)
    is_resolved = Column(Boolean, nullable=False, server_default=text("false"))
    is_reprocessed = Column(
        Boolean, server_default=text("false")
    )  # should be null if file hasn't been diverted

    patients = relationship(  # type:ignore
        PatientID, secondary=association_table
    )


class IssueType(Base):  # type:ignore
    __tablename__ = "issuetype"
    id = Column(Integer, primary_key=True)
    issue_type = Column(String(100), nullable=False)
