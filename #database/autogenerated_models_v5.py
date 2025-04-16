from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKeyConstraint, Index, Integer, JSON, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class Issuetype(Base):
    __tablename__ = 'issuetype'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='issuetype_pkey'),
        {'schema': 'investigations'}
    )

    id = mapped_column(Integer)
    issue_type = mapped_column(String(100), nullable=False)
    is_domain_issue = mapped_column(Boolean, nullable=False)

    issue: Mapped[List['Issue']] = relationship('Issue', uselist=True, back_populates='issue')


class Patientid(Base):
    __tablename__ = 'patientid'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='patientid_pkey'),
        Index('ix_investigations_patientid_pid', 'pid'),
        Index('ix_investigations_patientid_ukrdcid', 'ukrdcid'),
        {'schema': 'investigations'}
    )

    id = mapped_column(Integer)
    pid = mapped_column(String(50))
    ukrdcid = mapped_column(String(50))

    patientidtoissue: Mapped[List['Patientidtoissue']] = relationship('Patientidtoissue', uselist=True, back_populates='patient')


class Status(Base):
    __tablename__ = 'status'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='status_pkey'),
        {'schema': 'investigations'}
    )

    id = mapped_column(Integer)
    status = mapped_column(String(100), nullable=False)


class Xmlfile(Base):
    __tablename__ = 'xmlfile'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='xmlfile_pkey'),
        UniqueConstraint('file_hash', name='xmlfile_file_hash_key'),
        {'schema': 'investigations'}
    )

    id = mapped_column(Integer)
    file_hash = mapped_column(String(64), nullable=False)
    file = mapped_column(Text, nullable=False)
    is_reprocessed = mapped_column(Boolean, server_default=text('false'))

    issue: Mapped[List['Issue']] = relationship('Issue', uselist=True, back_populates='xml_file')


class Issue(Base):
    __tablename__ = 'issue'
    __table_args__ = (
        ForeignKeyConstraint(['issue_id'], ['investigations.issuetype.id'], name='issue_issue_id_fkey'),
        ForeignKeyConstraint(['xml_file_id'], ['investigations.xmlfile.id'], name='issue_xml_file_id_fkey'),
        PrimaryKeyConstraint('id', name='issue_pkey'),
        {'schema': 'investigations'}
    )

    id = mapped_column(Integer)
    date_created = mapped_column(DateTime, nullable=False)
    is_resolved = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_blocking = mapped_column(Boolean, nullable=False, server_default=text('true'))
    issue_id = mapped_column(Integer)
    error_message = mapped_column(Text)
    filename = mapped_column(String(100))
    xml_file_id = mapped_column(Integer)
    status_id = mapped_column(Integer, server_default=text('0'))
    priority = mapped_column(Integer)
    attributes = mapped_column(JSON)

    issue: Mapped[Optional['Issuetype']] = relationship('Issuetype', back_populates='issue')
    xml_file: Mapped[Optional['Xmlfile']] = relationship('Xmlfile', back_populates='issue')
    patientidtoissue: Mapped[List['Patientidtoissue']] = relationship('Patientidtoissue', uselist=True, back_populates='issue')


class Patientidtoissue(Base):
    __tablename__ = 'patientidtoissue'
    __table_args__ = (
        ForeignKeyConstraint(['issue_id'], ['investigations.issue.id'], name='patientidtoissue_issue_id_fkey'),
        ForeignKeyConstraint(['patient_id'], ['investigations.patientid.id'], name='patientidtoissue_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='patientidtoissue_pkey'),
        {'schema': 'investigations'}
    )

    id = mapped_column(Integer)
    patient_id = mapped_column(Integer)
    issue_id = mapped_column(Integer)
    rank = mapped_column(Integer)

    issue: Mapped[Optional['Issue']] = relationship('Issue', back_populates='patientidtoissue')
    patient: Mapped[Optional['Patientid']] = relationship('Patientid', back_populates='patientidtoissue')


from typing import List, Optional

from sqlalchemy import ARRAY, Boolean, Column, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, LargeBinary, Numeric, PrimaryKeyConstraint, String, Text, text
from sqlalchemy.dialects.postgresql import BIT
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class CodeExclusion(Base):
    __tablename__ = 'code_exclusion'
    __table_args__ = (
        PrimaryKeyConstraint('coding_standard', 'code', 'system', name='code_exclusion_pkey'),
        {'schema': 'extract'}
    )

    coding_standard = mapped_column(String, nullable=False)
    code = mapped_column(String, nullable=False)
    system = mapped_column(String, nullable=False)


class CodeList(Base):
    __tablename__ = 'code_list'
    __table_args__ = (
        PrimaryKeyConstraint('coding_standard', 'code', name='code_list_pkey'),
        {'schema': 'extract'}
    )

    coding_standard = mapped_column(String(256), nullable=False)
    code = mapped_column(String(256), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    description = mapped_column(String(256))
    object_type = mapped_column(String(256))
    update_date = mapped_column(DateTime)
    units = mapped_column(String(256))
    pkb_reference_range = mapped_column(String(10))
    pkb_comment = mapped_column(String(365))


class CodeMap(Base):
    __tablename__ = 'code_map'
    __table_args__ = (
        PrimaryKeyConstraint('source_coding_standard', 'source_code', 'destination_coding_standard', 'destination_code', name='code_map_pkey'),
        {'schema': 'extract'}
    )

    source_coding_standard = mapped_column(String(256), nullable=False)
    source_code = mapped_column(String(256), nullable=False)
    destination_coding_standard = mapped_column(String(256), nullable=False)
    destination_code = mapped_column(String(256), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    update_date = mapped_column(DateTime)


class Facility(Base):
    __tablename__ = 'facility'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='facility_pkey'),
        {'schema': 'extract'}
    )

    code = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pkb_out = mapped_column(Boolean, server_default=text('false'))
    pkb_in = mapped_column(Boolean, server_default=text('false'))
    pkb_msg_exclusions = mapped_column(ARRAY(Text()))
    update_date = mapped_column(DateTime)


class Locations(Base):
    __tablename__ = 'locations'
    __table_args__ = (
        PrimaryKeyConstraint('centre_code', name='locations_pkey'),
        {'schema': 'extract'}
    )

    centre_code = mapped_column(String(10))
    centre_name = mapped_column(String(255))
    country_code = mapped_column(String(6))
    region_code = mapped_column(String(10))
    paed_unit = mapped_column(Integer)


class ModalityCodes(Base):
    __tablename__ = 'modality_codes'
    __table_args__ = (
        PrimaryKeyConstraint('registry_code', name='modality_codes_pkey'),
        {'schema': 'extract'}
    )

    registry_code = mapped_column(String(8))
    registry_code_type = mapped_column(String(3), nullable=False)
    acute = mapped_column(BIT(1), nullable=False)
    transfer_in = mapped_column(BIT(1), nullable=False)
    ckd = mapped_column(BIT(1), nullable=False)
    cons = mapped_column(BIT(1), nullable=False)
    rrt = mapped_column(BIT(1), nullable=False)
    end_of_care = mapped_column(BIT(1), nullable=False)
    is_imprecise = mapped_column(BIT(1), nullable=False)
    registry_code_desc = mapped_column(String(100))
    equiv_modality = mapped_column(String(8))
    nhsbt_transplant_type = mapped_column(String(4))
    transfer_out = mapped_column(BIT(1))


class Patientrecord(Base):
    __tablename__ = 'patientrecord'
    __table_args__ = (
        PrimaryKeyConstraint('pid', name='patientrecord_pkey'),
        Index('ix_patientrecord_ukrdcid', 'ukrdcid'),
        {'schema': 'extract'}
    )

    pid = mapped_column(String)
    sendingfacility = mapped_column(String(7), nullable=False)
    sendingextract = mapped_column(String(6), nullable=False)
    localpatientid = mapped_column(String(17), nullable=False)
    repositorycreationdate = mapped_column(DateTime, nullable=False)
    repositoryupdatedate = mapped_column(DateTime, nullable=False)
    migrated = mapped_column(Boolean, nullable=False, server_default=text('false'))
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    ukrdcid = mapped_column(String(10))
    channelname = mapped_column(String(50))
    channelid = mapped_column(String(50))
    extracttime = mapped_column(String(50))
    startdate = mapped_column(DateTime)
    stopdate = mapped_column(DateTime)
    schemaversion = mapped_column(String(50))
    update_date = mapped_column(DateTime)

    allergy: Mapped[List['Allergy']] = relationship('Allergy', uselist=True, back_populates='patientrecord')
    assessment: Mapped[List['Assessment']] = relationship('Assessment', uselist=True, back_populates='patientrecord')
    clinicalrelationship: Mapped[List['Clinicalrelationship']] = relationship('Clinicalrelationship', uselist=True, back_populates='patientrecord')
    diagnosis: Mapped[List['Diagnosis']] = relationship('Diagnosis', uselist=True, back_populates='patientrecord')
    dialysisprescription: Mapped[List['Dialysisprescription']] = relationship('Dialysisprescription', uselist=True, back_populates='patientrecord')
    dialysissession: Mapped[List['Dialysissession']] = relationship('Dialysissession', uselist=True, back_populates='patientrecord')
    document: Mapped[List['Document']] = relationship('Document', uselist=True, back_populates='patientrecord')
    encounter: Mapped[List['Encounter']] = relationship('Encounter', uselist=True, back_populates='patientrecord')
    familyhistory: Mapped[List['Familyhistory']] = relationship('Familyhistory', uselist=True, back_populates='patientrecord')
    laborder: Mapped[List['Laborder']] = relationship('Laborder', uselist=True, back_populates='patientrecord')
    medication: Mapped[List['Medication']] = relationship('Medication', uselist=True, back_populates='patientrecord')
    observation: Mapped[List['Observation']] = relationship('Observation', uselist=True, back_populates='patientrecord')
    optout: Mapped[List['Optout']] = relationship('Optout', uselist=True, back_populates='patientrecord')
    procedure: Mapped[List['Procedure']] = relationship('Procedure', uselist=True, back_populates='patientrecord')
    programmembership: Mapped[List['Programmembership']] = relationship('Programmembership', uselist=True, back_populates='patientrecord')
    pvdelete: Mapped[List['Pvdelete']] = relationship('Pvdelete', uselist=True, back_populates='patientrecord')
    socialhistory: Mapped[List['Socialhistory']] = relationship('Socialhistory', uselist=True, back_populates='patientrecord')
    survey: Mapped[List['Survey']] = relationship('Survey', uselist=True, back_populates='patientrecord')
    transplant: Mapped[List['Transplant']] = relationship('Transplant', uselist=True, back_populates='patientrecord')
    transplantlist: Mapped[List['Transplantlist']] = relationship('Transplantlist', uselist=True, back_populates='patientrecord')
    treatment: Mapped[List['Treatment']] = relationship('Treatment', uselist=True, back_populates='patientrecord')
    vascularaccess: Mapped[List['Vascularaccess']] = relationship('Vascularaccess', uselist=True, back_populates='patientrecord')


class RrCodes(Base):
    __tablename__ = 'rr_codes'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'rr_code', name='rr_codes_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String, nullable=False)
    rr_code = mapped_column(String, nullable=False)
    description_1 = mapped_column(String(255))
    description_2 = mapped_column(String(70))
    description_3 = mapped_column(String(60))
    old_value = mapped_column(String(10))
    old_value_2 = mapped_column(String(10))
    new_value = mapped_column(String(10))


class RrDataDefinition(Base):
    __tablename__ = 'rr_data_definition'
    __table_args__ = (
        PrimaryKeyConstraint('upload_key', 'TABLE_NAME', name='pk_upload_key_table_name'),
        {'schema': 'extract'}
    )

    upload_key = mapped_column(String(5), nullable=False)
    TABLE_NAME = mapped_column(String(30), nullable=False)
    field_name = mapped_column(String(30), nullable=False)
    code_id = mapped_column(String(10))
    mandatory = mapped_column(Numeric(1, 0))
    TYPE = mapped_column(String(1))
    alt_constraint = mapped_column(String(30))
    alt_desc = mapped_column(String(30))
    extra_val = mapped_column(String(1))
    error_type = mapped_column(Integer)
    paed_mand = mapped_column(Numeric(1, 0))
    ckd5_mand = mapped_column(Numeric(1, 0))
    dependant_field = mapped_column(String(30))
    alt_validation = mapped_column(String(30))
    file_prefix = mapped_column(String(20))
    load_min = mapped_column(Numeric(38, 4))
    load_max = mapped_column(Numeric(38, 4))
    remove_min = mapped_column(Numeric(38, 4))
    remove_max = mapped_column(Numeric(38, 4))
    in_month = mapped_column(Numeric(1, 0))
    aki_mand = mapped_column(Numeric(1, 0))
    rrt_mand = mapped_column(Numeric(1, 0))
    cons_mand = mapped_column(Numeric(1, 0))
    ckd4_mand = mapped_column(Numeric(1, 0))
    valid_before_dob = mapped_column(Numeric(1, 0))
    valid_after_dod = mapped_column(Numeric(1, 0))
    in_quarter = mapped_column(Numeric(1, 0))


class UkrdcOdsGpCodes(Base):
    __tablename__ = 'ukrdc_ods_gp_codes'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='ukrdc_ods_gp_codes_pkey'),
        {'schema': 'extract'}
    )

    code = mapped_column(String(8))
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    name = mapped_column(String(50))
    address1 = mapped_column(String(35))
    postcode = mapped_column(String(8))
    phone = mapped_column(String(12))
    type = mapped_column(Enum('GP', 'PRACTICE', name='gp_type'))
    update_date = mapped_column(DateTime)

    familydoctor: Mapped[List['Familydoctor']] = relationship('Familydoctor', uselist=True, foreign_keys='[Familydoctor.gpid]', back_populates='ukrdc_ods_gp_codes')
    familydoctor_: Mapped[List['Familydoctor']] = relationship('Familydoctor', uselist=True, foreign_keys='[Familydoctor.gppracticeid]', back_populates='ukrdc_ods_gp_codes_')


class Allergy(Base):
    __tablename__ = 'allergy'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='allergy_pid_fkey'),
        PrimaryKeyConstraint('id', name='allergy_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    allergycode = mapped_column(String(100))
    allergycodestd = mapped_column(String(100))
    allergydesc = mapped_column(String(100))
    allergycategorycode = mapped_column(String(100))
    allergycategorycodestd = mapped_column(String(100))
    allergycategorydesc = mapped_column(String(100))
    severitycode = mapped_column(String(100))
    severitycodestd = mapped_column(String(100))
    severitydesc = mapped_column(String(100))
    cliniciancode = mapped_column(String(100))
    cliniciancodestd = mapped_column(String(100))
    cliniciandesc = mapped_column(String(100))
    discoverytime = mapped_column(DateTime)
    confirmedtime = mapped_column(DateTime)
    commenttext = mapped_column(String(500))
    inactivetime = mapped_column(DateTime)
    freetextallergy = mapped_column(String(500))
    qualifyingdetails = mapped_column(String(500))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='allergy')


class Assessment(Base):
    __tablename__ = 'assessment'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='assessment_pid_fkey'),
        PrimaryKeyConstraint('id', name='assessment_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    update_date = mapped_column(DateTime)
    assessmentstart = mapped_column(DateTime)
    assessmentend = mapped_column(DateTime)
    assessmenttypecode = mapped_column(String(100))
    assessmenttypecodestd = mapped_column(String(100))
    assessmenttypecodedesc = mapped_column(String(100))
    assessmentoutcomecode = mapped_column(String(100))
    assessmentoutcomecodestd = mapped_column(String(100))
    assessmentoutcomecodedesc = mapped_column(String(100))

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='assessment')


class Causeofdeath(Patientrecord):
    __tablename__ = 'causeofdeath'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='causeofdeath_pid_fkey'),
        PrimaryKeyConstraint('pid', name='causeofdeath_pkey'),
        {'schema': 'extract'}
    )

    pid = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    diagnosistype = mapped_column(String(50))
    diagnosingcliniciancode = mapped_column(String(100))
    diagnosingcliniciancodestd = mapped_column(String(100))
    diagnosingcliniciandesc = mapped_column(String(100))
    diagnosiscode = mapped_column(String(100))
    diagnosiscodestd = mapped_column(String(100))
    diagnosisdesc = mapped_column(String(255))
    comments = mapped_column(Text)
    enteredon = mapped_column(DateTime)
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)
    verificationstatus = mapped_column(String)


class Clinicalrelationship(Base):
    __tablename__ = 'clinicalrelationship'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='clinicalrelationship_pid_fkey'),
        PrimaryKeyConstraint('id', name='clinicalrelationship_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    cliniciancode = mapped_column(String(100))
    cliniciancodestd = mapped_column(String(100))
    cliniciandesc = mapped_column(String(100))
    facilitycode = mapped_column(String(100))
    facilitycodestd = mapped_column(String(100))
    facilitydesc = mapped_column(String(100))
    fromtime = mapped_column(Date)
    totime = mapped_column(Date)
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='clinicalrelationship')


class Diagnosis(Base):
    __tablename__ = 'diagnosis'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='diagnosis_pid_fkey'),
        PrimaryKeyConstraint('id', name='diagnosis_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    diagnosistype = mapped_column(String(50))
    diagnosingcliniciancode = mapped_column(String(100))
    diagnosingcliniciancodestd = mapped_column(String(100))
    diagnosingcliniciandesc = mapped_column(String(100))
    diagnosiscode = mapped_column(String(100))
    diagnosiscodestd = mapped_column(String(100))
    diagnosisdesc = mapped_column(String(255))
    comments = mapped_column(Text)
    identificationtime = mapped_column(DateTime)
    onsettime = mapped_column(DateTime)
    enteredon = mapped_column(DateTime)
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    encounternumber = mapped_column(String(100))
    biopsyperformed = mapped_column(String)
    verificationstatus = mapped_column(String)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='diagnosis')


class Dialysisprescription(Base):
    __tablename__ = 'dialysisprescription'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='dialysisprescription_pid_fkey'),
        PrimaryKeyConstraint('id', name='dialysisprescription_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    update_date = mapped_column(DateTime)
    enteredon = mapped_column(DateTime)
    fromtime = mapped_column(DateTime)
    totime = mapped_column(DateTime)
    sessiontype = mapped_column(String(5))
    sessionsperweek = mapped_column(Integer)
    timedialysed = mapped_column(Integer)
    vascularaccess = mapped_column(String(5))

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='dialysisprescription')


class Dialysissession(Base):
    __tablename__ = 'dialysissession'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='dialysissession_pid_fkey'),
        PrimaryKeyConstraint('id', name='dialysissession_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    proceduretypecode = mapped_column(String(100))
    proceduretypecodestd = mapped_column(String(100))
    proceduretypedesc = mapped_column(String(100))
    cliniciancode = mapped_column(String(100))
    cliniciancodestd = mapped_column(String(100))
    cliniciandesc = mapped_column(String(100))
    proceduretime = mapped_column(DateTime)
    enteredbycode = mapped_column(String(100))
    enteredbycodestd = mapped_column(String(100))
    enteredbydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    qhd19 = mapped_column(String(255))
    qhd20 = mapped_column(String(255))
    qhd21 = mapped_column(String(255))
    qhd22 = mapped_column(String(255))
    qhd30 = mapped_column(String(255))
    qhd31 = mapped_column(String(255))
    qhd32 = mapped_column(String(255))
    qhd33 = mapped_column(String(255))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='dialysissession')


class Document(Base):
    __tablename__ = 'document'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='document_pid_fkey'),
        PrimaryKeyConstraint('id', name='document_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    repositoryupdatedate = mapped_column(DateTime, nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    documenttime = mapped_column(DateTime)
    notetext = mapped_column(Text)
    documenttypecode = mapped_column(String(100))
    documenttypecodestd = mapped_column(String(100))
    documenttypedesc = mapped_column(String(100))
    cliniciancode = mapped_column(String(100))
    cliniciancodestd = mapped_column(String(100))
    cliniciandesc = mapped_column(String(100))
    documentname = mapped_column(String(100))
    statuscode = mapped_column(String(100))
    statuscodestd = mapped_column(String(100))
    statusdesc = mapped_column(String(100))
    enteredbycode = mapped_column(String(100))
    enteredbycodestd = mapped_column(String(100))
    enteredbydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    filetype = mapped_column(String(100))
    filename = mapped_column(String(100))
    stream = mapped_column(LargeBinary)
    documenturl = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='document')


class Encounter(Base):
    __tablename__ = 'encounter'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='encounter_pid_fkey'),
        PrimaryKeyConstraint('id', name='encounter_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    encounternumber = mapped_column(String(100))
    encountertype = mapped_column(String(100))
    fromtime = mapped_column(DateTime)
    totime = mapped_column(DateTime)
    admittingcliniciancode = mapped_column(String(100))
    admittingcliniciancodestd = mapped_column(String(100))
    admittingcliniciandesc = mapped_column(String(100))
    admitreasoncode = mapped_column(String(100))
    admitreasoncodestd = mapped_column(String(100))
    admitreasondesc = mapped_column(String(100))
    admissionsourcecode = mapped_column(String(100))
    admissionsourcecodestd = mapped_column(String(100))
    admissionsourcedesc = mapped_column(String(100))
    dischargereasoncode = mapped_column(String(100))
    dischargereasoncodestd = mapped_column(String(100))
    dischargereasondesc = mapped_column(String(100))
    dischargelocationcode = mapped_column(String(100))
    dischargelocationcodestd = mapped_column(String(100))
    dischargelocationdesc = mapped_column(String(100))
    healthcarefacilitycode = mapped_column(String(100))
    healthcarefacilitycodestd = mapped_column(String(100))
    healthcarefacilitydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    visitdescription = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='encounter')


class Familyhistory(Base):
    __tablename__ = 'familyhistory'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='familyhistory_pid_fkey'),
        PrimaryKeyConstraint('id', name='familyhistory_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    familymembercode = mapped_column(String(100))
    familymembercodestd = mapped_column(String(100))
    familymemberdesc = mapped_column(String(100))
    diagnosiscode = mapped_column(String(100))
    diagnosiscodestd = mapped_column(String(100))
    diagnosisdesc = mapped_column(String(100))
    notetext = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    fromtime = mapped_column(DateTime)
    totime = mapped_column(DateTime)
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='familyhistory')


class Laborder(Base):
    __tablename__ = 'laborder'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='laborder_pid_fkey'),
        PrimaryKeyConstraint('id', name='laborder_pkey'),
        Index('ix_laborder_creation_date', 'creation_date'),
        Index('ix_laborder_repository_update_date', 'repository_update_date'),
        Index('ix_laborder_update_date', 'update_date'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    placerid = mapped_column(String(100))
    fillerid = mapped_column(String(100))
    receivinglocationcode = mapped_column(String(100))
    receivinglocationcodestd = mapped_column(String(100))
    receivinglocationdesc = mapped_column(String(100))
    orderedbycode = mapped_column(String(100))
    orderedbycodestd = mapped_column(String(100))
    orderedbydesc = mapped_column(String(100))
    orderitemcode = mapped_column(String(100))
    orderitemcodestd = mapped_column(String(100))
    orderitemdesc = mapped_column(String(100))
    prioritycode = mapped_column(String(100))
    prioritycodestd = mapped_column(String(100))
    prioritydesc = mapped_column(String(100))
    status = mapped_column(String(100))
    ordercategorycode = mapped_column(String(100))
    ordercategorycodestd = mapped_column(String(100))
    ordercategorydesc = mapped_column(String(100))
    specimensource = mapped_column(String(50))
    specimenreceivedtime = mapped_column(DateTime)
    specimencollectedtime = mapped_column(DateTime)
    duration = mapped_column(String(50))
    patientclasscode = mapped_column(String(100))
    patientclasscodestd = mapped_column(String(100))
    patientclassdesc = mapped_column(String(100))
    enteredon = mapped_column(DateTime)
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    enteringorganizationcode = mapped_column(String(100))
    enteringorganizationcodestd = mapped_column(String(100))
    enteringorganizationdesc = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)
    repository_update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='laborder')
    resultitem: Mapped[List['Resultitem']] = relationship('Resultitem', uselist=True, back_populates='laborder')


class Medication(Base):
    __tablename__ = 'medication'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='medication_pid_fkey'),
        PrimaryKeyConstraint('id', name='medication_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    repositoryupdatedate = mapped_column(DateTime, nullable=False)
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    prescriptionnumber = mapped_column(String(100))
    fromtime = mapped_column(DateTime)
    totime = mapped_column(DateTime)
    orderedbycode = mapped_column(String(100))
    orderedbycodestd = mapped_column(String(100))
    orderedbydesc = mapped_column(String(100))
    enteringorganizationcode = mapped_column(String(100))
    enteringorganizationcodestd = mapped_column(String(100))
    enteringorganizationdesc = mapped_column(String(100))
    routecode = mapped_column(String(10))
    routecodestd = mapped_column(String(100))
    routedesc = mapped_column(String(100))
    drugproductidcode = mapped_column(String(100))
    drugproductidcodestd = mapped_column(String(100))
    drugproductiddesc = mapped_column(String(100))
    drugproductgeneric = mapped_column(String(255))
    drugproductlabelname = mapped_column(String(255))
    drugproductformcode = mapped_column(String(100))
    drugproductformcodestd = mapped_column(String(100))
    drugproductformdesc = mapped_column(String(100))
    drugproductstrengthunitscode = mapped_column(String(100))
    drugproductstrengthunitscodestd = mapped_column(String(100))
    drugproductstrengthunitsdesc = mapped_column(String(100))
    frequency = mapped_column(String(255))
    commenttext = mapped_column(String(1000))
    dosequantity = mapped_column(Numeric(19, 2))
    doseuomcode = mapped_column(String(100))
    doseuomcodestd = mapped_column(String(100))
    doseuomdesc = mapped_column(String(100))
    indication = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)
    encounternumber = mapped_column(String(100))

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='medication')


class Observation(Base):
    __tablename__ = 'observation'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='observation_pid_fkey'),
        PrimaryKeyConstraint('id', name='observation_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    observationtime = mapped_column(DateTime)
    observationcode = mapped_column(String(100))
    observationcodestd = mapped_column(String(100))
    observationdesc = mapped_column(String(100))
    observationvalue = mapped_column(String(100))
    observationunits = mapped_column(String(100))
    prepost = mapped_column(String(4))
    commenttext = mapped_column(String(100))
    cliniciancode = mapped_column(String(100))
    cliniciancodestd = mapped_column(String(100))
    cliniciandesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    enteringorganizationcode = mapped_column(String(100))
    enteringorganizationcodestd = mapped_column(String(100))
    enteringorganizationdesc = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='observation')


class Optout(Base):
    __tablename__ = 'optout'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='optout_pid_fkey'),
        PrimaryKeyConstraint('id', name='optout_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    programname = mapped_column(String(100))
    programdescription = mapped_column(String(100))
    enteredbycode = mapped_column(String(100))
    enteredbycodestd = mapped_column(String(100))
    enteredbydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    fromtime = mapped_column(Date)
    totime = mapped_column(Date)
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='optout')


class Patient(Patientrecord):
    __tablename__ = 'patient'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='patient_pid_fkey'),
        PrimaryKeyConstraint('pid', name='patient_pkey'),
        {'schema': 'extract'}
    )

    pid = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    birthtime = mapped_column(DateTime)
    deathtime = mapped_column(DateTime)
    gender = mapped_column(String(2))
    countryofbirth = mapped_column(String(3))
    ethnicgroupcode = mapped_column(String(100))
    ethnicgroupcodestd = mapped_column(String(100))
    ethnicgroupdesc = mapped_column(String(100))
    occupationcode = mapped_column(String(100))
    occupationcodestd = mapped_column(String(100))
    occupationdesc = mapped_column(String(100))
    primarylanguagecode = mapped_column(String(100))
    primarylanguagecodestd = mapped_column(String(100))
    primarylanguagedesc = mapped_column(String(100))
    death = mapped_column(Boolean)
    persontocontactname = mapped_column(String(100))
    persontocontact_relationship = mapped_column(String(20))
    persontocontact_contactnumber = mapped_column(String(20))
    persontocontact_contactnumbertype = mapped_column(String(20))
    persontocontact_contactnumbercomments = mapped_column(String(200))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    bloodgroup = mapped_column(String(100))
    bloodrhesus = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    address: Mapped[List['Address']] = relationship('Address', uselist=True, back_populates='patient')
    contactdetail: Mapped[List['Contactdetail']] = relationship('Contactdetail', uselist=True, back_populates='patient')
    name: Mapped[List['Name']] = relationship('Name', uselist=True, back_populates='patient')
    patientnumber: Mapped[List['Patientnumber']] = relationship('Patientnumber', uselist=True, back_populates='patient')


class Procedure(Base):
    __tablename__ = 'procedure'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='procedure_pid_fkey'),
        PrimaryKeyConstraint('id', name='procedure_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    proceduretypecode = mapped_column(String(100))
    proceduretypecodestd = mapped_column(String(100))
    proceduretypedesc = mapped_column(String(100))
    cliniciancode = mapped_column(String(100))
    cliniciancodestd = mapped_column(String(100))
    cliniciandesc = mapped_column(String(100))
    proceduretime = mapped_column(DateTime)
    enteredbycode = mapped_column(String(100))
    enteredbycodestd = mapped_column(String(100))
    enteredbydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='procedure')


class Programmembership(Base):
    __tablename__ = 'programmembership'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='programmembership_pid_fkey'),
        PrimaryKeyConstraint('id', name='programmembership_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    programname = mapped_column(String(100))
    programdescription = mapped_column(String(100))
    enteredbycode = mapped_column(String(100))
    enteredbycodestd = mapped_column(String(100))
    enteredbydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    fromtime = mapped_column(Date)
    totime = mapped_column(Date)
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='programmembership')


class Pvdata(Patientrecord):
    __tablename__ = 'pvdata'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['extract.patientrecord.pid'], name='pvdata_id_fkey'),
        PrimaryKeyConstraint('id', name='pvdata_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    update_date = mapped_column(DateTime)
    diagnosisdate = mapped_column(Date)
    bloodgroup = mapped_column(String(10))
    rrtstatus = mapped_column(String(100))
    tpstatus = mapped_column(String(100))


class Pvdelete(Base):
    __tablename__ = 'pvdelete'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='pvdelete_pid_fkey'),
        PrimaryKeyConstraint('did', name='pvdelete_pkey'),
        {'schema': 'extract'}
    )

    did = mapped_column(Integer)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    observationtime = mapped_column(DateTime)
    serviceidcode = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='pvdelete')


class Renaldiagnosis(Patientrecord):
    __tablename__ = 'renaldiagnosis'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='renaldiagnosis_pid_fkey'),
        PrimaryKeyConstraint('pid', name='renaldiagnosis_pkey'),
        {'schema': 'extract'}
    )

    pid = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    diagnosistype = mapped_column(String(50))
    diagnosiscode = mapped_column(String)
    diagnosiscodestd = mapped_column(String)
    diagnosisdesc = mapped_column(String)
    diagnosingcliniciancode = mapped_column(String(100))
    diagnosingcliniciancodestd = mapped_column(String(100))
    diagnosingcliniciandesc = mapped_column(String(100))
    comments = mapped_column(String)
    identificationtime = mapped_column(DateTime)
    onsettime = mapped_column(DateTime)
    enteredon = mapped_column(DateTime)
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)
    biopsyperformed = mapped_column(String)
    verificationstatus = mapped_column(String)


class Socialhistory(Base):
    __tablename__ = 'socialhistory'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='socialhistory_pid_fkey'),
        PrimaryKeyConstraint('id', name='socialhistory_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    socialhabitcode = mapped_column(String(100))
    socialhabitcodestd = mapped_column(String(100))
    socialhabitdesc = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='socialhistory')


class Survey(Base):
    __tablename__ = 'survey'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='survey_pid_fkey'),
        PrimaryKeyConstraint('id', name='survey_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    surveytime = mapped_column(DateTime, nullable=False)
    pid = mapped_column(String)
    surveytypecode = mapped_column(String(100))
    surveytypecodestd = mapped_column(String(100))
    surveytypedesc = mapped_column(String(100))
    typeoftreatment = mapped_column(String(100))
    hdlocation = mapped_column(String(100))
    template = mapped_column(String(100))
    enteredbycode = mapped_column(String(100))
    enteredbycodestd = mapped_column(String(100))
    enteredbydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='survey')
    level: Mapped[List['Level']] = relationship('Level', uselist=True, back_populates='survey')
    question: Mapped[List['Question']] = relationship('Question', uselist=True, back_populates='survey')
    score: Mapped[List['Score']] = relationship('Score', uselist=True, back_populates='survey')


class Transplant(Base):
    __tablename__ = 'transplant'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='transplant_pid_fkey'),
        PrimaryKeyConstraint('id', name='transplant_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    proceduretypecode = mapped_column(String(100))
    proceduretypecodestd = mapped_column(String(100))
    proceduretypedesc = mapped_column(String(100))
    cliniciancode = mapped_column(String(100))
    cliniciancodestd = mapped_column(String(100))
    cliniciandesc = mapped_column(String(100))
    proceduretime = mapped_column(DateTime)
    enteredbycode = mapped_column(String(100))
    enteredbycodestd = mapped_column(String(100))
    enteredbydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    tra64 = mapped_column(DateTime)
    tra65 = mapped_column(String(255))
    tra66 = mapped_column(String(255))
    tra69 = mapped_column(DateTime)
    tra76 = mapped_column(String(255))
    tra77 = mapped_column(String(255))
    tra78 = mapped_column(String(255))
    tra79 = mapped_column(String(255))
    tra80 = mapped_column(String(255))
    tra8a = mapped_column(String(255))
    tra81 = mapped_column(String(255))
    tra82 = mapped_column(String(255))
    tra83 = mapped_column(String(255))
    tra84 = mapped_column(String(255))
    tra85 = mapped_column(String(255))
    tra86 = mapped_column(String(255))
    tra87 = mapped_column(String(255))
    tra88 = mapped_column(String(255))
    tra89 = mapped_column(String(255))
    tra90 = mapped_column(String(255))
    tra91 = mapped_column(String(255))
    tra92 = mapped_column(String(255))
    tra93 = mapped_column(String(255))
    tra94 = mapped_column(String(255))
    tra95 = mapped_column(String(255))
    tra96 = mapped_column(String(255))
    tra97 = mapped_column(String(255))
    tra98 = mapped_column(String(255))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='transplant')


class Transplantlist(Base):
    __tablename__ = 'transplantlist'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='transplantlist_pid_fkey'),
        PrimaryKeyConstraint('id', name='transplantlist_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    encounternumber = mapped_column(String(100))
    encountertype = mapped_column(String(100))
    fromtime = mapped_column(DateTime)
    totime = mapped_column(DateTime)
    admittingcliniciancode = mapped_column(String(100))
    admittingcliniciancodestd = mapped_column(String(100))
    admittingcliniciandesc = mapped_column(String(100))
    admitreasoncode = mapped_column(String(100))
    admitreasoncodestd = mapped_column(String(100))
    admitreasondesc = mapped_column(String(100))
    admissionsourcecode = mapped_column(String(100))
    admissionsourcecodestd = mapped_column(String(100))
    admissionsourcedesc = mapped_column(String(100))
    dischargereasoncode = mapped_column(String(100))
    dischargereasoncodestd = mapped_column(String(100))
    dischargereasondesc = mapped_column(String(100))
    dischargelocationcode = mapped_column(String(100))
    dischargelocationcodestd = mapped_column(String(100))
    dischargelocationdesc = mapped_column(String(100))
    healthcarefacilitycode = mapped_column(String(100))
    healthcarefacilitycodestd = mapped_column(String(100))
    healthcarefacilitydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    visitdescription = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='transplantlist')


class Treatment(Base):
    __tablename__ = 'treatment'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='treatment_pid_fkey'),
        PrimaryKeyConstraint('id', name='treatment_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    encounternumber = mapped_column(String(100))
    encountertype = mapped_column(String(100))
    fromtime = mapped_column(DateTime)
    totime = mapped_column(DateTime)
    admittingcliniciancode = mapped_column(String(100))
    admittingcliniciancodestd = mapped_column(String(100))
    admittingcliniciandesc = mapped_column(String(100))
    admitreasoncode = mapped_column(String(100))
    admitreasoncodestd = mapped_column(String(100))
    admitreasondesc = mapped_column(String(100))
    admissionsourcecode = mapped_column(String(100))
    admissionsourcecodestd = mapped_column(String(100))
    admissionsourcedesc = mapped_column(String(100))
    dischargereasoncode = mapped_column(String(100))
    dischargereasoncodestd = mapped_column(String(100))
    dischargereasondesc = mapped_column(String(100))
    dischargelocationcode = mapped_column(String(100))
    dischargelocationcodestd = mapped_column(String(100))
    dischargelocationdesc = mapped_column(String(100))
    healthcarefacilitycode = mapped_column(String(100))
    healthcarefacilitycodestd = mapped_column(String(100))
    healthcarefacilitydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    visitdescription = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    hdp01 = mapped_column(String(255))
    hdp02 = mapped_column(String(255))
    hdp03 = mapped_column(String(255))
    hdp04 = mapped_column(String(255))
    qbl05 = mapped_column(String(255))
    qbl06 = mapped_column(String(255))
    qbl07 = mapped_column(String(255))
    erf61 = mapped_column(String(255))
    pat35 = mapped_column(String(255))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='treatment')


class Vascularaccess(Base):
    __tablename__ = 'vascularaccess'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patientrecord.pid'], name='vascularaccess_pid_fkey'),
        PrimaryKeyConstraint('id', name='vascularaccess_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    proceduretypecode = mapped_column(String(100))
    proceduretypecodestd = mapped_column(String(100))
    proceduretypedesc = mapped_column(String(100))
    cliniciancode = mapped_column(String(100))
    cliniciancodestd = mapped_column(String(100))
    cliniciandesc = mapped_column(String(100))
    proceduretime = mapped_column(DateTime)
    enteredbycode = mapped_column(String(100))
    enteredbycodestd = mapped_column(String(100))
    enteredbydesc = mapped_column(String(100))
    enteredatcode = mapped_column(String(100))
    enteredatcodestd = mapped_column(String(100))
    enteredatdesc = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    acc19 = mapped_column(String(255))
    acc20 = mapped_column(String(255))
    acc21 = mapped_column(String(255))
    acc22 = mapped_column(String(255))
    acc30 = mapped_column(String(255))
    acc40 = mapped_column(String(255))
    update_date = mapped_column(DateTime)

    patientrecord: Mapped[Optional['Patientrecord']] = relationship('Patientrecord', back_populates='vascularaccess')


class Address(Base):
    __tablename__ = 'address'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patient.pid'], name='address_pid_fkey'),
        PrimaryKeyConstraint('id', name='address_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    addressuse = mapped_column(String(10))
    fromtime = mapped_column(Date)
    totime = mapped_column(Date)
    street = mapped_column(String(100))
    town = mapped_column(String(100))
    county = mapped_column(String(100))
    postcode = mapped_column(String(10))
    countrycode = mapped_column(String(100))
    countrycodestd = mapped_column(String(100))
    countrydesc = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patient: Mapped[Optional['Patient']] = relationship('Patient', back_populates='address')


class Contactdetail(Base):
    __tablename__ = 'contactdetail'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patient.pid'], name='contactdetail_pid_fkey'),
        PrimaryKeyConstraint('id', name='contactdetail_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    contactuse = mapped_column(String(10))
    contactvalue = mapped_column(String(100))
    commenttext = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patient: Mapped[Optional['Patient']] = relationship('Patient', back_populates='contactdetail')


class Familydoctor(Patient):
    __tablename__ = 'familydoctor'
    __table_args__ = (
        ForeignKeyConstraint(['gpid'], ['extract.ukrdc_ods_gp_codes.code'], name='familydoctor_gpid_fkey'),
        ForeignKeyConstraint(['gppracticeid'], ['extract.ukrdc_ods_gp_codes.code'], name='familydoctor_gppracticeid_fkey'),
        ForeignKeyConstraint(['id'], ['extract.patient.pid'], name='familydoctor_id_fkey'),
        PrimaryKeyConstraint('id', name='familydoctor_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    gpname = mapped_column(String(100))
    gpid = mapped_column(String(20))
    gppracticeid = mapped_column(String(20))
    addressuse = mapped_column(String(10))
    fromtime = mapped_column(Date)
    totime = mapped_column(Date)
    street = mapped_column(String(100))
    town = mapped_column(String(100))
    county = mapped_column(String(100))
    postcode = mapped_column(String(10))
    countrycode = mapped_column(String(100))
    countrycodestd = mapped_column(String(100))
    countrydesc = mapped_column(String(100))
    contactuse = mapped_column(String(10))
    contactvalue = mapped_column(String(100))
    email = mapped_column(String(100))
    commenttext = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    ukrdc_ods_gp_codes: Mapped[Optional['UkrdcOdsGpCodes']] = relationship('UkrdcOdsGpCodes', foreign_keys=[gpid], back_populates='familydoctor')
    ukrdc_ods_gp_codes_: Mapped[Optional['UkrdcOdsGpCodes']] = relationship('UkrdcOdsGpCodes', foreign_keys=[gppracticeid], back_populates='familydoctor_')


class Level(Base):
    __tablename__ = 'level'
    __table_args__ = (
        ForeignKeyConstraint(['surveyid'], ['extract.survey.id'], name='level_surveyid_fkey'),
        PrimaryKeyConstraint('id', name='level_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    surveyid = mapped_column(String)
    idx = mapped_column(Integer)
    levelvalue = mapped_column(String(100))
    leveltypecode = mapped_column(String(100))
    leveltypecodestd = mapped_column(String(100))
    leveltypedesc = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    survey: Mapped[Optional['Survey']] = relationship('Survey', back_populates='level')


class Name(Base):
    __tablename__ = 'name'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patient.pid'], name='name_pid_fkey'),
        PrimaryKeyConstraint('id', name='name_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    nameuse = mapped_column(String(10))
    prefix = mapped_column(String(10))
    family = mapped_column(String(60))
    given = mapped_column(String(60))
    othergivennames = mapped_column(String(60))
    suffix = mapped_column(String(10))
    update_date = mapped_column(DateTime)

    patient: Mapped[Optional['Patient']] = relationship('Patient', back_populates='name')


class Patientnumber(Base):
    __tablename__ = 'patientnumber'
    __table_args__ = (
        ForeignKeyConstraint(['pid'], ['extract.patient.pid'], name='patientnumber_pid_fkey'),
        PrimaryKeyConstraint('id', name='patientnumber_pkey'),
        Index('ix_patientnumber_patientid', 'patientid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pid = mapped_column(String)
    idx = mapped_column(Integer)
    patientid = mapped_column(String(50))
    numbertype = mapped_column(String(3))
    organization = mapped_column(String(50))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    patient: Mapped[Optional['Patient']] = relationship('Patient', back_populates='patientnumber')


class Question(Base):
    __tablename__ = 'question'
    __table_args__ = (
        ForeignKeyConstraint(['surveyid'], ['extract.survey.id'], name='question_surveyid_fkey'),
        PrimaryKeyConstraint('id', name='question_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    surveyid = mapped_column(String)
    idx = mapped_column(Integer)
    questiontypecode = mapped_column(String(100))
    questiontypecodestd = mapped_column(String(100))
    questiontypedesc = mapped_column(String(100))
    response = mapped_column(String(100))
    questiontext = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    survey: Mapped[Optional['Survey']] = relationship('Survey', back_populates='question')


class Resultitem(Base):
    __tablename__ = 'resultitem'
    __table_args__ = (
        ForeignKeyConstraint(['orderid'], ['extract.laborder.id'], name='resultitem_orderid_fkey'),
        PrimaryKeyConstraint('id', name='resultitem_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    orderid = mapped_column(String)
    resulttype = mapped_column(String(2))
    serviceidcode = mapped_column(String(100))
    serviceidcodestd = mapped_column(String(100))
    serviceiddesc = mapped_column(String(100))
    subid = mapped_column(String(50))
    resultvalue = mapped_column(String(20))
    resultvalueunits = mapped_column(String(30))
    referencerange = mapped_column(String(30))
    interpretationcodes = mapped_column(String(50))
    status = mapped_column(String(5))
    observationtime = mapped_column(DateTime)
    commenttext = mapped_column(String(1000))
    referencecomment = mapped_column(String(1000))
    prepost = mapped_column(String(4))
    enteredon = mapped_column(DateTime)
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    laborder: Mapped[Optional['Laborder']] = relationship('Laborder', back_populates='resultitem')


class Score(Base):
    __tablename__ = 'score'
    __table_args__ = (
        ForeignKeyConstraint(['surveyid'], ['extract.survey.id'], name='score_surveyid_fkey'),
        PrimaryKeyConstraint('id', name='score_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    surveyid = mapped_column(String)
    idx = mapped_column(Integer)
    scorevalue = mapped_column(String(100))
    scoretypecode = mapped_column(String(100))
    scoretypecodestd = mapped_column(String(100))
    scoretypedesc = mapped_column(String(100))
    update_date = mapped_column(DateTime)

    survey: Mapped[Optional['Survey']] = relationship('Survey', back_populates='score')
