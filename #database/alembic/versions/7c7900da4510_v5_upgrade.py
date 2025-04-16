"""v5 dataset changes. This is chatGPT generated attempt to convert the sql
migration to alembic. I suspect it wouldn't be too much effort shaping this
into working code but I don't see any point really. 

Revision ID: 7c7900da4510
Revises: a1a7539b1a57
Create Date: 2024-12-05 17:24:26.102851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c7900da4510'
down_revision: Union[str, None] = 'a1a7539b1a57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

def upgrade():
    # Create tables in "extract" schema
    op.create_table(
        'assessment',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('pid', sa.String(), nullable=True),
        sa.Column('creation_date', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('update_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('assessmentstart', sa.TIMESTAMP(), nullable=True),
        sa.Column('assessmentend', sa.TIMESTAMP(), nullable=True),
        sa.Column('assessmenttypecode', sa.String(length=100), nullable=True),
        sa.Column('assessmenttypecodestd', sa.String(length=100), nullable=True),
        sa.Column('assessmenttypecodedesc', sa.String(length=100), nullable=True),
        sa.Column('assessmentoutcomecode', sa.String(length=100), nullable=True),
        sa.Column('assessmentoutcomecodestd', sa.String(length=100), nullable=True),
        sa.Column('assessmentoutcomecodedesc', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='extract'
    )

    op.alter_column('patientrecord', 'channelid', new_column_name='latestfilehash', schema='extract')

    # Add columns to existing tables
    op.add_column('causeofdeath', sa.Column('verificationstatus', sa.String(length=100)), schema='extract')
    op.add_column('diagnosis', sa.Column('verificationstatus', sa.String(length=100)), schema='extract')
    op.add_column('renaldiagnosis', sa.Column('biopsyperformed', sa.String(length=100)), schema='extract')
    op.add_column('renaldiagnosis', sa.Column('verificationstatus', sa.String(length=100)), schema='extract')

    # Create additional tables
    op.create_table(
        'dialysisprescription',
        sa.Column('id', sa.String(length=20), nullable=False),
        sa.Column('pid', sa.String(length=20), nullable=True),
        sa.Column('creation_date', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('update_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('enteredon', sa.TIMESTAMP(), nullable=True),
        sa.Column('fromtime', sa.TIMESTAMP(), nullable=True),
        sa.Column('totime', sa.TIMESTAMP(), nullable=True),
        sa.Column('sessiontype', sa.String(length=5), nullable=True),
        sa.Column('sessionsperweek', sa.Integer(), nullable=True),
        sa.Column('timedialysed', sa.Integer(), nullable=True),
        sa.Column('vascularaccess', sa.String(length=5), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='extract'
    )

    op.create_table(
        'vascularaccess',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('pid', sa.String(), nullable=True),
        sa.Column('idx', sa.Integer(), nullable=True),
        sa.Column('creation_date', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('proceduretypecode', sa.String(length=100), nullable=True),
        sa.Column('proceduretypecodestd', sa.String(length=100), nullable=True),
        sa.Column('proceduretypedesc', sa.String(length=100), nullable=True),
        sa.Column('cliniciancode', sa.String(length=100), nullable=True),
        sa.Column('cliniciancodestd', sa.String(length=100), nullable=True),
        sa.Column('cliniciandesc', sa.String(length=100), nullable=True),
        sa.Column('proceduretime', sa.TIMESTAMP(), nullable=True),
        sa.Column('enteredbycode', sa.String(length=100), nullable=True),
        sa.Column('enteredbycodestd', sa.String(length=100), nullable=True),
        sa.Column('enteredbydesc', sa.String(length=100), nullable=True),
        sa.Column('enteredatcode', sa.String(length=100), nullable=True),
        sa.Column('enteredatcodestd', sa.String(length=100), nullable=True),
        sa.Column('enteredatdesc', sa.String(length=100), nullable=True),
        sa.Column('updatedon', sa.TIMESTAMP(), nullable=True),
        sa.Column('actioncode', sa.String(length=3), nullable=True),
        sa.Column('externalid', sa.String(length=100), nullable=True),
        sa.Column('acc19', sa.String(length=255), nullable=True),
        sa.Column('acc20', sa.String(length=255), nullable=True),
        sa.Column('acc21', sa.String(length=255), nullable=True),
        sa.Column('acc22', sa.String(length=255), nullable=True),
        sa.Column('acc30', sa.String(length=255), nullable=True),
        sa.Column('acc40', sa.String(length=255), nullable=True),
        sa.Column('update_date', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='extract'
    )

    # Create "investigations" schema
    op.execute('CREATE SCHEMA IF NOT EXISTS investigations')

    op.create_table(
        'issue',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('issue_id', sa.Integer, nullable=True),
        sa.Column('date_created', sa.TIMESTAMP(), nullable=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('filename', sa.String(length=100), nullable=True),
        sa.Column('xml_file_id', sa.Integer, nullable=True),
        sa.Column('is_resolved', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_blocking', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('status_id', sa.Integer, server_default=sa.text('0'), nullable=True),
        sa.Column('priority', sa.Integer, nullable=True),
        sa.Column('attributes', JSON, nullable=True),
        schema='investigations'
    )

    op.create_table(
        'issuetype',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('issue_type', sa.String(length=100), nullable=False),
        sa.Column('is_domain_issue', sa.Boolean(), nullable=False),
        schema='investigations'
    )

    op.create_table(
        'patientid',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('pid', sa.String(length=50), nullable=True),
        sa.Column('ukrdcid', sa.String(length=50), nullable=True),
        schema='investigations'
    )

    op.create_table(
        'patientidtoissue',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('patient_id', sa.Integer, nullable=True),
        sa.Column('issue_id', sa.Integer, nullable=True),
        sa.Column('rank', sa.Integer, nullable=True),
        schema='investigations'
    )

    op.create_table(
        'status',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('status', sa.String(length=100), nullable=False),
        schema='investigations'
    )

    op.create_table(
        'xmlfile',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('file', sa.Text, nullable=False),
        sa.Column('is_reprocessed', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        schema='investigations'
    )

    # Create sequences
    op.execute("CREATE SEQUENCE investigations.issue_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1")
    op.execute("CREATE SEQUENCE investigations.issuetype_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1")
    op.execute("CREATE SEQUENCE investigations.patientid_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1")
    op.execute("CREATE SEQUENCE investigations.patientidtoissue_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1")
    op.execute("CREATE SEQUENCE investigations.status_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1")
    op.execute("CREATE SEQUENCE investigations.xmlfile_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1")

    # Set default values for IDs
    op.execute("ALTER TABLE ONLY investigations.issue ALTER COLUMN id SET DEFAULT nextval('investigations.issue_id_seq'::regclass)")
    op.execute("ALTER TABLE ONLY investigations.issuetype ALTER COLUMN id SET DEFAULT nextval('investigations.issuetype_id_seq'::regclass)")
    op.execute("ALTER TABLE ONLY investigations.patientid ALTER COLUMN id SET DEFAULT nextval('investigations.patientid_id_seq'::regclass)")
    op.execute("ALTER TABLE ONLY investigations.patientidtoissue ALTER COLUMN id SET DEFAULT nextval('investigations.patientidtoissue_id_seq'::regclass)")
    op.execute("ALTER TABLE ONLY investigations.status ALTER COLUMN id SET DEFAULT nextval('investigations.status_id_seq'::regclass)")
    op.execute("ALTER TABLE ONLY investigations.xmlfile ALTER COLUMN id SET DEFAULT nextval('investigations.xmlfile_id_seq'::regclass)")

    # Create foreign key relationships
    op.create_foreign_key("issue_issue_id_fkey", "issue", "issuetype", ["issue_id"], ["id"], schema="investigations")
    op.create_foreign_key("issue_xml_file_id_fkey", "issue", "xmlfile", ["xml_file_id"], ["id"], schema="investigations")
    op.create_foreign_key("patientidtoissue_issue_id_fkey", "patientidtoissue", "issue", ["issue_id"], ["id"], schema="investigations")
    op.create_foreign_key("patientidtoissue_patient_id_fkey", "patientidtoissue", "patientid", ["patient_id"], ["id"], schema="investigations")

def downgrade():
    # Drop foreign key relationships
    op.drop_constraint("patientidtoissue_patient_id_fkey", "patientidtoissue", schema="investigations", type_="foreignkey")
    op.drop_constraint("patientidtoissue_issue_id_fkey", "patientidtoissue", schema="investigations", type_="foreignkey")
    op.drop_constraint("issue_xml_file_id_fkey", "issue", schema="investigations", type_="foreignkey")
    op.drop_constraint("issue_issue_id_fkey", "issue", schema="investigations", type_="foreignkey")

    # Drop sequences
    op.execute("DROP SEQUENCE investigations.issue_id_seq")
    op.execute("DROP SEQUENCE investigations.issuetype_id_seq")
    op.execute("DROP SEQUENCE investigations.patientid_id_seq")
    op.execute("DROP SEQUENCE investigations.patientidtoissue_id_seq")
    op.execute("DROP SEQUENCE investigations.status_id_seq")
    op.execute("DROP SEQUENCE investigations.xmlfile_id_seq")

    # Drop tables
    op.drop_table('xmlfile', schema='investigations')
    op.drop_table('status', schema='investigations')
    op.drop_table('patientidtoissue', schema='investigations')
    op.drop_table('patientid', schema='investigations')
    op.drop_table('issuetype', schema='investigations')
    op.drop_table('issue', schema='investigations')

    op.drop_table('vascularaccess', schema='extract')
    op.drop_table('dialysisprescription', schema='extract')

    op.drop_column('renaldiagnosis', 'verificationstatus', schema='extract')
    op.drop_column('renaldiagnosis', 'biopsyperformed', schema='extract')
    op.drop_column('diagnosis', 'verificationstatus', schema='extract')
    op.drop_column('causeofdeath', 'verificationstatus', schema='extract')

    op.alter_column('patientrecord', 'latestfilehash', new_column_name='channelid', schema='extract')

    op.drop_table('assessment', schema='extract')

    # Drop schema
    op.execute('DROP SCHEMA IF EXISTS investigations CASCADE')
