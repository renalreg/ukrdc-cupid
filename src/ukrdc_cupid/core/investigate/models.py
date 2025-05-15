""" Models for the investigations. Since the decision has been made to include
these models in the ukrdc they should really live in the ukrdc-sqla repo. 
"""

from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import (
    MetaData,
    Column,
    Integer,
    Boolean,
    String,
    JSON,
    DateTime,
    Text,
    ForeignKey,
    Table,
    text,
)


metadata = MetaData(schema="investigations")
Base = declarative_base(metadata=metadata)

GLOBAL_LAZY = "dynamic"

# Many to many relationship exists between pateint ids
# (internal such as ukrdc and external such as NHS)
# this table allows a issue_id to allow multiple patientids to be appended to any particular issue
# similarly it makes it easy to look up which issues are already accosiated with a particular id.

LinkPatientToIssue = Table(
    "patientidtoissue",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("patient_id", Integer, ForeignKey("patientid.id")),
    Column("issue_id", Integer, ForeignKey("issue.id")),
    Column("rank", Integer, nullable=True),
)


class Issue(Base):  # type:ignore
    __tablename__ = "issue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey("issuetype.id"))

    date_created = Column(DateTime, nullable=False)
    error_message = Column(Text)
    filename = Column(String(100))
    xml_file_id = Column(Integer, ForeignKey("xmlfile.id"))
    is_resolved = Column(Boolean, nullable=False, server_default=text("false"))
    is_blocking = Column(Boolean, nullable=False, server_default=text("true"))

    # Mirroring Jira board statuses (e.g. Open, Closed, Waiting for Unit, Pending Discussion etc)
    status_id = Column(Integer, nullable=True, server_default=text("0"))

    # This creates scope for automated functions to produce low priority investigations
    priority = Column(Integer, nullable=True)

    # This should contain any attributes required to fully investigate issue
    # In particular it should contain the items of data which generated
    # investigation
    attributes = Column(JSON, nullable=True)

    patients = relationship(  # type:ignore
        "PatientID", secondary=LinkPatientToIssue, back_populates="issues"
    )
    xml_file = relationship("XmlFile", back_populates="issues")


class PatientID(Base):  # type:ignore
    __tablename__ = "patientid"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(String(50), index=True, nullable=True)
    ukrdcid = Column(String(50), index=True)

    issues = relationship(  # type:ignore
        Issue,
        secondary=LinkPatientToIssue,
        back_populates="patients",
        overlaps="patients",
    )


class Status(Base):
    __tablename__ = "status"
    id = Column(Integer, primary_key=True)
    status = Column(String(100), nullable=False)


class IssueType(Base):  # type:ignore
    __tablename__ = "issuetype"
    id = Column(Integer, primary_key=True)
    issue_type = Column(String(100), nullable=False)
    is_domain_issue = Column(Boolean, nullable=False)


class XmlFile(Base):
    # Table contains files that get held up by cupid because cupid has
    # generated an investigation against it we may want to make it more
    # sophisticated like splitting out sentdate before applying uniqueness
    __tablename__ = "xmlfile"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_hash = Column(String(64), nullable=False, unique=True)
    file = Column(Text, nullable=False)
    is_reprocessed = Column(
        Boolean, server_default=text("false")
    )  # has the file been merged

    issues = relationship(Issue, back_populates="xml_file")
