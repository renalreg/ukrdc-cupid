from sqlalchemy import ARRAY, Boolean, CHAR, Column, Date, DateTime, Index, Integer, LargeBinary, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import BIT, ENUM
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.orm.base import Mapped

Base = declarative_base()
metadata = Base.metadata


class Address(Base):
    __tablename__ = 'address'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='address_pkey'),
        Index('ix_address_pid', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Allergy(Base):
    __tablename__ = 'allergy'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='allergy_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Causeofdeath(Base):
    __tablename__ = 'causeofdeath'
    __table_args__ = (
        PrimaryKeyConstraint('pid', name='causeofdeath_pkey'),
        {'schema': 'extract'}
    )

    pid = mapped_column(String(30))
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


class Clinicalrelationship(Base):
    __tablename__ = 'clinicalrelationship'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='clinicalrelationship_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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
    pkb_comment = mapped_column(Text)


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


class Contactdetail(Base):
    __tablename__ = 'contactdetail'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='contactdetail_pkey'),
        Index('ix_contactdetail_pid', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    idx = mapped_column(Integer)
    contactuse = mapped_column(String(10))
    contactvalue = mapped_column(String(100))
    commenttext = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)


class Diagnosis(Base):
    __tablename__ = 'diagnosis'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='diagnosis_pkey'),
        Index('ix_diagnosis_pid', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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
    verificationstatus = mapped_column(String(100))


class Dialysissession(Base):
    __tablename__ = 'dialysissession'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='dialysissession_pkey'),
        Index('ix_dialysissession_pid', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Document(Base):
    __tablename__ = 'document'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='document_pkey'),
        Index('ix_document_pid', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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
    repositoryupdatedate = mapped_column(DateTime)
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)


class Encounter(Base):
    __tablename__ = 'encounter'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='encounter_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Eventcontrol(Base):
    __tablename__ = 'eventcontrol'
    __table_args__ = (
        PrimaryKeyConstraint('eventtype', name='eventcontrol_pkey'),
        {'schema': 'extract'}
    )

    eventtype = mapped_column(CHAR(20))
    eventdate = mapped_column(DateTime, nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pendingeventdate = mapped_column(DateTime)
    update_date = mapped_column(DateTime)


class Facility(Base):
    __tablename__ = 'facility'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='pk_facility'),
        {'schema': 'extract'}
    )

    code = mapped_column(String(256))
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    pkb_out = mapped_column(Boolean, server_default=text('false'))
    pkb_in = mapped_column(Boolean, server_default=text('false'))
    pkb_msg_exclusions = mapped_column(ARRAY(Text()))
    update_date = mapped_column(DateTime)
    ukrdc_out_pkb = mapped_column(Boolean, server_default=text('false'))
    pv_out_pkb = mapped_column(Boolean, server_default=text('false'))


class Familydoctor(Base):
    __tablename__ = 'familydoctor'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='familydoctor_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
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


class Familyhistory(Base):
    __tablename__ = 'familyhistory'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='familyhistory_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Laborder(Base):
    __tablename__ = 'laborder'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='laborder_pkey'),
        Index('laborder_pid_idx', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Level(Base):
    __tablename__ = 'level'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='level_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    surveyid = mapped_column(String(100), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    idx = mapped_column(Integer)
    levelvalue = mapped_column(String(100))
    leveltypecode = mapped_column(String(100))
    leveltypecodestd = mapped_column(String(100))
    leveltypedesc = mapped_column(String(100))
    update_date = mapped_column(DateTime)


t_locations = Table(
    'locations', metadata,
    Column('centre_code', String(10), nullable=False),
    Column('centre_name', String(255), nullable=False),
    Column('country_code', String(6), nullable=False),
    Column('region_code', String(10)),
    Column('paed_unit', Integer, nullable=False),
    schema='extract'
)


class Medication(Base):
    __tablename__ = 'medication'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='medication_pkey'),
        Index('medication_pid_idx', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(150))
    pid = mapped_column(String(30), nullable=False)
    repositoryupdatedate = mapped_column(DateTime, nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


t_modality_codes = Table(
    'modality_codes', metadata,
    Column('registry_code', String(8), nullable=False),
    Column('registry_code_desc', String(100)),
    Column('registry_code_type', String(3), nullable=False),
    Column('acute', BIT(1), nullable=False),
    Column('transfer_in', BIT(1), nullable=False),
    Column('ckd', BIT(1), nullable=False),
    Column('cons', BIT(1), nullable=False),
    Column('rrt', BIT(1), nullable=False),
    Column('equiv_modality', String(8)),
    Column('end_of_care', BIT(1), nullable=False),
    Column('is_imprecise', BIT(1), nullable=False),
    Column('nhsbt_transplant_type', String(4)),
    Column('transfer_out', BIT(1)),
    schema='extract'
)


class Name(Base):
    __tablename__ = 'name'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='name_pkey'),
        Index('name_pid_idx', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    idx = mapped_column(Integer)
    nameuse = mapped_column(String(10))
    prefix = mapped_column(String(10))
    family = mapped_column(String(60))
    given = mapped_column(String(60))
    othergivennames = mapped_column(String(60))
    suffix = mapped_column(String(10))
    update_date = mapped_column(DateTime)


class Observation(Base):
    __tablename__ = 'observation'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='observation_pkey'),
        Index('ix_observation_pid_obstime', 'pid', 'observationtime'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Optout(Base):
    __tablename__ = 'optout'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='optout_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Patient(Base):
    __tablename__ = 'patient'
    __table_args__ = (
        PrimaryKeyConstraint('pid', name='patient_pkey'),
        {'schema': 'extract'}
    )

    pid = mapped_column(String(30))
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


class Patientnumber(Base):
    __tablename__ = 'patientnumber'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='patientnumber_pkey'),
        Index('patientnumber_patientid', 'patientid'),
        Index('patientnumber_pid_idx', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    idx = mapped_column(Integer)
    patientid = mapped_column(String(50))
    numbertype = mapped_column(String(3))
    organization = mapped_column(String(50))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)


class Patientrecord(Base):
    __tablename__ = 'patientrecord'
    __table_args__ = (
        PrimaryKeyConstraint('pid', name='patientrecord_pkey'),
        UniqueConstraint('sendingfacility', 'sendingextract', 'localpatientid', name='patientrecord_key2'),
        Index('ix_patientrecord_ukrdcid', 'ukrdcid'),
        Index('patientrecord_sendingextract_ix', 'sendingextract'),
        Index('patientrecord_sendingfacility_ix', 'sendingfacility'),
        {'schema': 'extract'}
    )

    pid = mapped_column(String(30))
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


class PkbLinks(Base):
    __tablename__ = 'pkb_links'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pkb_links_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(Integer)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    link = mapped_column(String)
    link_name = mapped_column(String)
    coding_standard = mapped_column(String)
    code = mapped_column(String)
    update_date = mapped_column(DateTime)


class Procedure(Base):
    __tablename__ = 'procedure'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='procedure_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Programmembership(Base):
    __tablename__ = 'programmembership'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='programmembership_pkey'),
        Index('ix_programmembership_pid', 'pid'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Pvdata(Base):
    __tablename__ = 'pvdata'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pvdata_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    rrtstatus = mapped_column(String(100))
    tpstatus = mapped_column(String(100))
    diagnosisdate = mapped_column(Date)
    bloodgroup = mapped_column(String(10))
    update_date = mapped_column(DateTime)


class Pvdelete(Base):
    __tablename__ = 'pvdelete'
    __table_args__ = (
        PrimaryKeyConstraint('did', name='pvdelete_pkey'),
        Index('ix_pvdelete_pid', 'pid'),
        {'schema': 'extract'}
    )

    did = mapped_column(Integer)
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    observationtime = mapped_column(DateTime)
    serviceidcode = mapped_column(String(100))
    update_date = mapped_column(DateTime)


class Question(Base):
    __tablename__ = 'question'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='question_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    surveyid = mapped_column(String(100), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    idx = mapped_column(Integer)
    questiontypecode = mapped_column(String(100))
    questiontypecodestd = mapped_column(String(100))
    questiontypedesc = mapped_column(String(100))
    response = mapped_column(String(100))
    questiontext = mapped_column(String(100))
    update_date = mapped_column(DateTime)


class Renaldiagnosis(Base):
    __tablename__ = 'renaldiagnosis'
    __table_args__ = (
        PrimaryKeyConstraint('pid', name='renaldiagnosis_pkey'),
        {'schema': 'extract'}
    )

    pid = mapped_column(String(30))
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Resultitem(Base):
    __tablename__ = 'resultitem'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='resultitem_pkey'),
        Index('resultitem_observationtime', 'observationtime'),
        Index('resultitem_orderid_firstpart'),
        Index('resultitem_orderid_idx', 'orderid'),
        Index('resultitem_orderid_idx_hash', 'orderid'),
        Index('resultitem_serviceidcode', 'serviceidcode'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    orderid = mapped_column(String(100), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    resulttype = mapped_column(String(2))
    serviceidcode = mapped_column(String(100))
    serviceidcodestd = mapped_column(String(100))
    serviceiddesc = mapped_column(String(100))
    subid = mapped_column(String(50))
    resultvalue = mapped_column(String(30))
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


t_rr_codes = Table(
    'rr_codes', metadata,
    Column('id', String(10), nullable=False),
    Column('rr_code', String(10), nullable=False),
    Column('description_1', String(255)),
    Column('description_2', String(70)),
    Column('description_3', String(60)),
    Column('old_value', String(10)),
    Column('old_value_2', String(10)),
    Column('new_value', String(10)),
    schema='extract'
)


t_rr_data_definition = Table(
    'rr_data_definition', metadata,
    Column('upload_key', String(5)),
    Column('TABLE_NAME', String(30), nullable=False),
    Column('field_name', String(30), nullable=False),
    Column('code_id', String(10)),
    Column('mandatory', Numeric(1, 0)),
    Column('TYPE', String(1)),
    Column('alt_constraint', String(30)),
    Column('alt_desc', String(30)),
    Column('extra_val', String(1)),
    Column('error_type', Integer),
    Column('paed_mand', Numeric(1, 0)),
    Column('ckd5_mand', Numeric(1, 0)),
    Column('dependant_field', String(30)),
    Column('alt_validation', String(30)),
    Column('file_prefix', String(20)),
    Column('load_min', Numeric(38, 4)),
    Column('load_max', Numeric(38, 4)),
    Column('remove_min', Numeric(38, 4)),
    Column('remove_max', Numeric(38, 4)),
    Column('in_month', Numeric(1, 0)),
    Column('aki_mand', Numeric(1, 0)),
    Column('rrt_mand', Numeric(1, 0)),
    Column('cons_mand', Numeric(1, 0)),
    Column('ckd4_mand', Numeric(1, 0)),
    Column('valid_before_dob', Numeric(1, 0)),
    Column('valid_after_dod', Numeric(1, 0)),
    Column('in_quarter', Numeric(1, 0)),
    schema='extract'
)


class SatelliteMap(Base):
    __tablename__ = 'satellite_map'
    __table_args__ = (
        PrimaryKeyConstraint('satellite_code', 'main_unit_code', name='satellite_map_pkey'),
        {'schema': 'extract'}
    )

    satellite_code = mapped_column(String(10), nullable=False)
    main_unit_code = mapped_column(String(10), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    update_date = mapped_column(DateTime)


class Score(Base):
    __tablename__ = 'score'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='score_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    surveyid = mapped_column(String(100), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    idx = mapped_column(Integer)
    scorevalue = mapped_column(String(100))
    scoretypecode = mapped_column(String(100))
    scoretypecodestd = mapped_column(String(100))
    scoretypedesc = mapped_column(String(100))
    update_date = mapped_column(DateTime)


class Socialhistory(Base):
    __tablename__ = 'socialhistory'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='socialhistory_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    idx = mapped_column(Integer)
    socialhabitcode = mapped_column(String(100))
    socialhabitcodestd = mapped_column(String(100))
    socialhabitdesc = mapped_column(String(100))
    updatedon = mapped_column(DateTime)
    actioncode = mapped_column(String(3))
    externalid = mapped_column(String(100))
    update_date = mapped_column(DateTime)


class Survey(Base):
    __tablename__ = 'survey'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='survey_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    surveytime = mapped_column(DateTime, nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Transplant(Base):
    __tablename__ = 'transplant'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='transplant_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Transplantlist(Base):
    __tablename__ = 'transplantlist'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='transplantlist_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


class Treatment(Base):
    __tablename__ = 'treatment'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='treatment_pkey'),
        Index('ix_treatment_pid', 'pid'),
        Index('ix_treatment_pid_fromtime', 'pid', 'fromtime'),
        Index('treatment_fromtime_ix', 'fromtime'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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
    visitdescription = mapped_column(String(255))
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


class UkrdcOdsGpCodes(Base):
    __tablename__ = 'ukrdc_ods_gp_codes'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='pk_ukrdc_ods_gp_codes'),
        {'schema': 'extract'}
    )

    code = mapped_column(String(8))
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    name = mapped_column(String(50))
    address1 = mapped_column(String(35))
    postcode = mapped_column(String(8))
    phone = mapped_column(String(12))
    type = mapped_column(ENUM('gp_type', 'GP', 'PRACTICE', name='gp_type'))
    update_date = mapped_column(DateTime)


class Validationerror(Base):
    __tablename__ = 'validationerror'
    __table_args__ = (
        PrimaryKeyConstraint('vid', name='validationerror_pkey'),
        {'schema': 'extract'}
    )

    vid = mapped_column(Integer)
    pid = mapped_column(String(30), nullable=False)
    errortype = mapped_column(Integer, nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updatedon = mapped_column(DateTime)
    message = mapped_column(String(200))
    update_date = mapped_column(DateTime)


class Vascularaccess(Base):
    __tablename__ = 'vascularaccess'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='vascularaccess_pkey'),
        {'schema': 'extract'}
    )

    id = mapped_column(String(100))
    pid = mapped_column(String(30), nullable=False)
    creation_date = mapped_column(DateTime, nullable=False, server_default=text('now()'))
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


t_vwe_extract_myrenalcare_updates = Table(
    'vwe_extract_myrenalcare_updates', metadata,
    Column('pid', String(30)),
    Column('id', Text),
    Column('msg_type', Text),
    schema='extract'
)


t_vwe_extract_pkb = Table(
    'vwe_extract_pkb', metadata,
    Column('pid', String(30)),
    Column('id', Text),
    Column('msg_type', Text),
    schema='extract'
)


t_vwe_extract_pkb_deceased = Table(
    'vwe_extract_pkb_deceased', metadata,
    Column('ukrdcid', String(10)),
    schema='extract'
)


t_vwe_extract_pkb_deceased_test = Table(
    'vwe_extract_pkb_deceased_test', metadata,
    Column('ukrdcid', String(10)),
    schema='extract'
)


t_vwe_extract_pkb_full = Table(
    'vwe_extract_pkb_full', metadata,
    Column('pid', String(30)),
    Column('id', Text),
    Column('msg_type', Text),
    schema='extract'
)


t_vwe_extract_pkb_new = Table(
    'vwe_extract_pkb_new', metadata,
    Column('ukrdcid', String(10)),
    schema='extract'
)


t_vwe_extract_pkb_new_test = Table(
    'vwe_extract_pkb_new_test', metadata,
    Column('ukrdcid', String(10)),
    schema='extract'
)


t_vwe_extract_pkb_updates = Table(
    'vwe_extract_pkb_updates', metadata,
    Column('pid', String(30)),
    Column('id', Text),
    Column('msg_type', Text),
    schema='extract'
)


t_vwe_extract_pv_pvxml = Table(
    'vwe_extract_pv_pvxml', metadata,
    Column('pid', String(30)),
    schema='extract'
)


t_vwe_extract_pv_pvxml_eligable = Table(
    'vwe_extract_pv_pvxml_eligable', metadata,
    Column('pid', String(30)),
    schema='extract'
)


t_vwe_extract_pv_rda = Table(
    'vwe_extract_pv_rda', metadata,
    Column('pid', String(30)),
    schema='extract'
)


t_vwe_extract_radar = Table(
    'vwe_extract_radar', metadata,
    Column('pid', String(30)),
    schema='extract'
)


t_vwe_myrenalcare_members = Table(
    'vwe_myrenalcare_members', metadata,
    Column('ukrdcid', String(10)),
    schema='extract'
)


t_vwe_pkb_changes = Table(
    'vwe_pkb_changes', metadata,
    Column('pid', String),
    Column('id', Text),
    Column('msg_type', Text),
    schema='extract'
)


t_vwe_pkb_members = Table(
    'vwe_pkb_members', metadata,
    Column('ukrdcid', String(10)),
    schema='extract'
)


t_vwe_pkb_test_patients = Table(
    'vwe_pkb_test_patients', metadata,
    Column('pid', String(30)),
    schema='extract'
)


t_vwe_pv_members = Table(
    'vwe_pv_members', metadata,
    Column('ukrdcid', String(10)),
    schema='extract'
)


t_vwe_survey_data = Table(
    'vwe_survey_data', metadata,
    Column('pid', String(30)),
    Column('sendingfacility', String(7)),
    Column('sendingfacility_desc', String(256)),
    Column('main_unit_code', String(10)),
    Column('main_unit_desc', String(256)),
    Column('repositorycreationdate', DateTime),
    Column('NHS Number', String(50)),
    Column('forename', String(60)),
    Column('surname', String(60)),
    Column('dob', DateTime),
    Column('ethnicity', String(100)),
    Column('gender', String(2)),
    Column('Post Code', String(10)),
    Column('Date Completed', DateTime),
    Column('enteredatcode', String(100)),
    Column('ysq1', Text),
    Column('ysq2', Text),
    Column('ysq3', Text),
    Column('ysq4', Text),
    Column('ysq5', Text),
    Column('ysq6', Text),
    Column('ysq7', Text),
    Column('ysq8', Text),
    Column('ysq9', Text),
    Column('ysq10', Text),
    Column('ysq11', Text),
    Column('ysq12', Text),
    Column('ysq13', Text),
    Column('ysq14', Text),
    Column('ysq15', Text),
    Column('ysq16', Text),
    Column('ysq17', Text),
    Column('yohq1', Text),
    Column('yohq2', Text),
    Column('yohq3', Text),
    Column('yohq4', Text),
    Column('yohq5', Text),
    Column('myhq1', Text),
    Column('myhq2', Text),
    Column('myhq3', Text),
    Column('myhq4', Text),
    Column('myhq5', Text),
    Column('myhq6', Text),
    Column('myhq7', Text),
    Column('myhq8', Text),
    Column('myhq9', Text),
    Column('myhq10', Text),
    Column('myhq11', Text),
    Column('myhq12', Text),
    Column('myhq13', Text),
    Column('pam_13_score', Text),
    Column('pam_13_level', Text),
    Column('shq1', Text),
    Column('shq2', Text),
    Column('shq3', Text),
    Column('shq4', Text),
    Column('shq5', Text),
    Column('shq6', Text),
    Column('shq7', Text),
    Column('shq8', Text),
    Column('shq9', Text),
    Column('shq10', Text),
    Column('shq11', Text),
    Column('shq12', Text),
    Column('shq13', Text),
    Column('shq14', Text),
    Column('shq15', Text),
    Column('shq16', Text),
    Column('shq17', Text),
    Column('yhs1', Text),
    Column('yhs2', Text),
    Column('yhs3', Text),
    Column('yhs4', Text),
    Column('yhs5', Text),
    Column('yhs6', Text),
    Column('yhs', Text),
    Column('shd', Text),
    Column('lcc', Text),
    schema='extract'
)
