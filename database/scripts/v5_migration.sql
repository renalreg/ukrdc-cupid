CREATE TABLE "extract".assessment (
    id character varying NOT NULL,
    pid character varying,
    creation_date timestamp without time zone DEFAULT now() NOT NULL,
    update_date timestamp without time zone,
    assessmentstart timestamp without time zone,
    assessmentend timestamp without time zone,
    assessmenttypecode character varying(100),
    assessmenttypecodestd character varying(100),
    assessmenttypecodedesc character varying(100),
    assessmentoutcomecode character varying(100),
    assessmentoutcomecodestd character varying(100),
    assessmentoutcomecodedesc character varying(100)
);


ALTER TABLE "extract".assessment OWNER TO ukrdc;
-- address NO CHANGE
-- allergy NO CHANGE
ALTER TABLE "extract".causeofdeath
ADD COLUMN verificationstatus character varying(100);
-- clinical relationship no change 
-- code exclusion 
-- code_list
-- code_map
-- contactdetail
ALTER TABLE "extract".diagnosis
ADD COLUMN verificationstatus character varying(100);

CREATE TABLE "extract".dialysisprescription (
    id character varying(20),
    pid character varying(20),
    creation_date timestamp without time zone DEFAULT now() NOT NULL,
    update_date timestamp without time zone,
    enteredon timestamp without time zone,
    fromtime timestamp without time zone,
    totime timestamp without time zone,
    sessiontype character varying(5),
    sessionsperweek integer,
    timedialysed integer,
    vascularaccess character varying(5)
);
ALTER TABLE "extract".dialysisprescription OWNER TO ukrdc;
--dialysissession
--document
--encounter
--table event control no sqla models
--table facility sqla models incomplete
--familydoctor
--familyhistory
--laborder
--level
--locations
--medication
--modality_codes
--name
--observation
--optout
--patient
--patientnumber
-- reuse empty column to contain a hash of the most recent file
ALTER TABLE "extract".patientrecord 
RENAME COLUMN channelid TO latestfilehash;
--pkb links table is not covered by the sqlalchemy models
--procedure
--programmembership
--pvdata
--pvdelete
--pvdelete_did_seq
--question
ALTER TABLE "extract".renaldiagnosis
ADD COLUMN biopsyperformed character varying(100),
ADD COLUMN verificationstatus character varying(100);


--resultitem
--rr_codes
--rr_data_definition
-- SatelliteMap seems to be missing from v5 models? 
--score
--socialhistory
--survey
--transplant
--transplantlist
--treatment
--ukrdc_ods_gp_codes


CREATE TABLE "extract".vascularaccess (
    id character varying NOT NULL,
    pid character varying,
    idx integer,
    creation_date timestamp without time zone DEFAULT now() NOT NULL,
    proceduretypecode character varying(100),
    proceduretypecodestd character varying(100),
    proceduretypedesc character varying(100),
    cliniciancode character varying(100),
    cliniciancodestd character varying(100),
    cliniciandesc character varying(100),
    proceduretime timestamp without time zone,
    enteredbycode character varying(100),
    enteredbycodestd character varying(100),
    enteredbydesc character varying(100),
    enteredatcode character varying(100),
    enteredatcodestd character varying(100),
    enteredatdesc character varying(100),
    updatedon timestamp without time zone,
    actioncode character varying(3),
    externalid character varying(100),
    acc19 character varying(255),
    acc20 character varying(255),
    acc21 character varying(255),
    acc22 character varying(255),
    acc30 character varying(255),
    acc40 character varying(255),
    update_date timestamp without time zone
);


ALTER TABLE "extract".vascularaccess OWNER TO ukrdc;







-- now we create the new investigations schema required for cupid
CREATE SCHEMA IF NOT EXISTS investigations;


CREATE TABLE investigations.issue (
    id integer NOT NULL,
    issue_id integer,
    date_created timestamp without time zone NOT NULL,
    error_message text,
    filename character varying(100),
    xml_file_id integer,
    is_resolved boolean DEFAULT false NOT NULL,
    is_blocking boolean DEFAULT true NOT NULL,
    status_id integer DEFAULT 0,
    priority integer,
    attributes json
);


ALTER TABLE investigations.issue OWNER TO ukrdc;


CREATE SEQUENCE investigations.issue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE investigations.issue_id_seq OWNER TO ukrdc;
ALTER SEQUENCE investigations.issue_id_seq OWNED BY investigations.issue.id;

CREATE TABLE investigations.issuetype (
    id integer NOT NULL,
    issue_type character varying(100) NOT NULL,
    is_domain_issue boolean NOT NULL
);

ALTER TABLE investigations.issuetype OWNER TO ukrdc;


CREATE SEQUENCE investigations.issuetype_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE investigations.issuetype_id_seq OWNER TO ukrdc;
ALTER SEQUENCE investigations.issuetype_id_seq OWNED BY investigations.issuetype.id;


CREATE TABLE investigations.patientid (
    id integer NOT NULL,
    pid character varying(50),
    ukrdcid character varying(50)
);


ALTER TABLE investigations.patientid OWNER TO ukrdc;
CREATE SEQUENCE investigations.patientid_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE investigations.patientid_id_seq OWNER TO ukrdc;


ALTER SEQUENCE investigations.patientid_id_seq OWNED BY investigations.patientid.id;
CREATE TABLE investigations.patientidtoissue (
    id integer NOT NULL,
    patient_id integer,
    issue_id integer,
    rank integer
);

ALTER TABLE investigations.patientidtoissue OWNER TO ukrdc;


CREATE SEQUENCE investigations.patientidtoissue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE investigations.patientidtoissue_id_seq OWNER TO ukrdc;
ALTER SEQUENCE investigations.patientidtoissue_id_seq OWNED BY investigations.patientidtoissue.id;
CREATE TABLE investigations.status (
    id integer NOT NULL,
    status character varying(100) NOT NULL
);


ALTER TABLE investigations.status OWNER TO ukrdc;
CREATE SEQUENCE investigations.status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE investigations.status_id_seq OWNER TO ukrdc;

ALTER SEQUENCE investigations.status_id_seq OWNED BY investigations.status.id;
CREATE TABLE investigations.xmlfile (
    id integer NOT NULL,
    file_hash character varying(64) NOT NULL,
    file text NOT NULL,
    is_reprocessed boolean DEFAULT false
);

ALTER TABLE investigations.xmlfile OWNER TO ukrdc;
CREATE SEQUENCE investigations.xmlfile_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE investigations.xmlfile_id_seq OWNER TO ukrdc;
ALTER SEQUENCE investigations.xmlfile_id_seq OWNED BY investigations.xmlfile.id;

-- new investigations keys
ALTER TABLE ONLY investigations.issue ALTER COLUMN id SET DEFAULT nextval('investigations.issue_id_seq'::regclass);
ALTER TABLE ONLY investigations.issuetype ALTER COLUMN id SET DEFAULT nextval('investigations.issuetype_id_seq'::regclass);
ALTER TABLE ONLY investigations.patientid ALTER COLUMN id SET DEFAULT nextval('investigations.patientid_id_seq'::regclass);
ALTER TABLE ONLY investigations.patientidtoissue ALTER COLUMN id SET DEFAULT nextval('investigations.patientidtoissue_id_seq'::regclass);
ALTER TABLE ONLY investigations.status ALTER COLUMN id SET DEFAULT nextval('investigations.status_id_seq'::regclass);
ALTER TABLE ONLY investigations.xmlfile ALTER COLUMN id SET DEFAULT nextval('investigations.xmlfile_id_seq'::regclass);


--new ukrdc keys 
ALTER TABLE ONLY "extract".assessment ADD CONSTRAINT assessment_pkey PRIMARY KEY (id);
ALTER TABLE ONLY "extract".dialysisprescription ADD CONSTRAINT dialysisprescription_pkey PRIMARY KEY (id);
ALTER TABLE ONLY "extract".vascularaccess ADD CONSTRAINT vascularaccess_pkey PRIMARY KEY (id);


--controversially we enable foreign key relationships
ALTER TABLE ONLY "extract".address ADD CONSTRAINT address_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patient(pid);
ALTER TABLE ONLY "extract".allergy ADD CONSTRAINT allergy_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".assessment ADD CONSTRAINT assessment_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".causeofdeath ADD CONSTRAINT causeofdeath_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".clinicalrelationship ADD CONSTRAINT clinicalrelationship_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".contactdetail ADD CONSTRAINT contactdetail_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patient(pid);
ALTER TABLE ONLY "extract".diagnosis ADD CONSTRAINT diagnosis_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".dialysisprescription ADD CONSTRAINT dialysisprescription_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".dialysissession ADD CONSTRAINT dialysissession_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".document ADD CONSTRAINT document_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".encounter ADD CONSTRAINT encounter_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".familydoctor ADD CONSTRAINT familydoctor_gpid_fkey FOREIGN KEY (gpid) REFERENCES "extract".ukrdc_ods_gp_codes(code);
ALTER TABLE ONLY "extract".familydoctor ADD CONSTRAINT familydoctor_gppracticeid_fkey FOREIGN KEY (gppracticeid) REFERENCES "extract".ukrdc_ods_gp_codes(code);
ALTER TABLE ONLY "extract".familydoctor ADD CONSTRAINT familydoctor_id_fkey FOREIGN KEY (id) REFERENCES "extract".patient(pid);
ALTER TABLE ONLY "extract".familyhistory ADD CONSTRAINT familyhistory_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".laborder ADD CONSTRAINT laborder_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".level ADD CONSTRAINT level_surveyid_fkey FOREIGN KEY (surveyid) REFERENCES "extract".survey(id);
ALTER TABLE ONLY "extract".medication ADD CONSTRAINT medication_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".name ADD CONSTRAINT name_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patient(pid);
ALTER TABLE ONLY "extract".observation ADD CONSTRAINT observation_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".optout ADD CONSTRAINT optout_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".patient ADD CONSTRAINT patient_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".patientnumber ADD CONSTRAINT patientnumber_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patient(pid);
ALTER TABLE ONLY "extract".procedure ADD CONSTRAINT procedure_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".programmembership ADD CONSTRAINT programmembership_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".pvdata ADD CONSTRAINT pvdata_id_fkey FOREIGN KEY (id) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".pvdelete ADD CONSTRAINT pvdelete_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".question ADD CONSTRAINT question_surveyid_fkey FOREIGN KEY (surveyid) REFERENCES "extract".survey(id);
ALTER TABLE ONLY "extract".renaldiagnosis ADD CONSTRAINT renaldiagnosis_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".resultitem ADD CONSTRAINT resultitem_orderid_fkey FOREIGN KEY (orderid) REFERENCES "extract".laborder(id);
ALTER TABLE ONLY "extract".score ADD CONSTRAINT score_surveyid_fkey FOREIGN KEY (surveyid) REFERENCES "extract".survey(id);
ALTER TABLE ONLY "extract".socialhistory ADD CONSTRAINT socialhistory_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".survey ADD CONSTRAINT survey_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".transplant ADD CONSTRAINT transplant_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".transplantlist ADD CONSTRAINT transplantlist_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".treatment ADD CONSTRAINT treatment_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);
ALTER TABLE ONLY "extract".vascularaccess ADD CONSTRAINT vascularaccess_pid_fkey FOREIGN KEY (pid) REFERENCES "extract".patientrecord(pid);

-- And the fk relationships in the investigations schema
ALTER TABLE ONLY investigations.issue ADD CONSTRAINT issue_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES investigations.issuetype(id);
ALTER TABLE ONLY investigations.issue ADD CONSTRAINT issue_xml_file_id_fkey FOREIGN KEY (xml_file_id) REFERENCES investigations.xmlfile(id);
ALTER TABLE ONLY investigations.patientidtoissue ADD CONSTRAINT patientidtoissue_issue_id_fkey FOREIGN KEY (issue_id) REFERENCES investigations.issue(id);
ALTER TABLE ONLY investigations.patientidtoissue ADD CONSTRAINT patientidtoissue_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES investigations.patientid(id);