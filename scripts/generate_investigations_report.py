import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values
from ukrdc_cupid.core.investigate.models import Issue, IssueType
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment

ENV = dotenv_values(".env.scripts")

# Establish a connection to the PostgreSQL database
DATABASE_URL = ENV["CUPID_URL"]
EXCEL_FILE_NAME = ".do_not_commit/investigations_issues.xlsx"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Query the database for issue types
issue_types = session.query(IssueType).all()

# Initialize a pandas Excel writer
with pd.ExcelWriter(EXCEL_FILE_NAME, engine="openpyxl") as writer:
    # Iterate through each issue type
    for issue_type in issue_types:
        # Fetch issues related to this issue type
        issues = session.query(Issue).filter(Issue.issue_id == issue_type.id).all()

        # Prepare data for the sheet
        data = []
        for issue in issues:
            # Fetch related patient ids
            patient_ids = [patient.pid for patient in issue.patients]

            # Gather all the required fields
            row = {
                "Issue ID": issue.id,
                "Patient IDs": ", ".join(patient_ids),  # Join list of patient ids
                "File ID": issue.xml_file_id,
                "Attributes (Metadata)": issue.attributes,
                "Error Message": issue.error_message,
            }
            data.append(row)

        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data)
        if len(df) > 0:
            df = df.sort_values(by=["Patient IDs", "File ID", "Issue ID"], ascending=[True, True, True])

        # Create a new DataFrame to add the issue type as a title at the top
        title_df = pd.DataFrame([[f"Issue Type: {issue_type.issue_type}"]], columns=[""])

        # Write the title row followed by the data to the sheet
        sheet_name = str(issue_type.id)  # Use issue_type ID as the sheet name
        title_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)

        # Access the worksheet object to apply formatting
        worksheet = writer.sheets[sheet_name]

        # Set text wrap for the "Attributes (Metadata)" and "Error Message" columns
        wrap_columns = ['D', 'E']  # Assuming "Attributes (Metadata)" is column D and "Error Message" is column E
        for col in wrap_columns:
            worksheet.column_dimensions[col].width = 50
            for row in range(3, len(df) + 3):  # Start from row 3 where the data begins
                cell = worksheet[f"{col}{row}"]
                cell.alignment = Alignment(wrap_text=True)

# Close the session
session.close()

print(f"Excel file created: {EXCEL_FILE_NAME}")
