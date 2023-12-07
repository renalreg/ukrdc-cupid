from sqlalchemy import create_engine
from ukrdc_cupid.core.investigate.models import Base

url = "postgresql://postgres:postgres@localhost:5432/dummy_ukrdc_investigations"
engine = create_engine(url, echo=True)

# Create the tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)