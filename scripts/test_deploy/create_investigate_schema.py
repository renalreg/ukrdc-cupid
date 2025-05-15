from sqlalchemy import create_engine
from ukrdc_cupid.core.investigate.models import Base
from ukrdc_cupid.core.utils import DatabaseConnection
from ukrdc_cupid.core.investigate.utils import update_issue_types

connector = DatabaseConnection(env_prefix="INVESTIGATE")
url = connector.generate_database_url()
engine = create_engine(url, echo=True)

# Create the tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

update_issue_types()