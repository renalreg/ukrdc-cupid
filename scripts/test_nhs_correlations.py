from sqlalchemy import select, create_engine, distinct, func, BigInteger
from sqlalchemy.orm import sessionmaker
from ukrdc_sqla.ukrdc import Patient, PatientNumber
import pandas as pd
from dotenv import dotenv_values
import plotly.express as px
from sqlalchemy.orm import Session

# Load environment variables and create engine
ENV = dotenv_values(".env.scripts")
ukrdc_live_url = ENV["UKRDC_URL"]

# Create session
ukrdc_live_engine = create_engine(ukrdc_live_url)
LiveSession = sessionmaker(bind=ukrdc_live_engine, autoflush=False, autocommit=False)
session = LiveSession()

# Run the query to get distinct birth_time and patientid combinations
query = (
    select(
        distinct(Patient.birth_time),
        func.cast(func.regexp_replace(PatientNumber.patientid, '[^0-9]', '', 'g'), BigInteger).label("patientid")
    )
    .join(PatientNumber, PatientNumber.pid == Patient.pid)
    .where(PatientNumber.organization == 'NHS')
    .limit(10000)
)
result = session.execute(query).fetchall()

# Convert the result into a DataFrame
df = pd.DataFrame(result, columns=['birth_time', 'patientid'])

# Convert birth_time to a datetime format (if needed) for accurate plotting
df['birth_time'] = pd.to_datetime(df['birth_time'])

# Generate the scatter plot
fig = px.scatter(df, x='birth_time', y='patientid', title='Correlation plot between Date of Birth and Patient ID')


