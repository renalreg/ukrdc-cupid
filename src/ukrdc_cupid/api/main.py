from fastapi import Depends, FastAPI, Request, HTTPException, Response
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string
from ukrdc_cupid.core.utils import UKRDCConnection
from ukrdc_cupid.core.store.insert import process_file

# from ukrdc_cupid.core.store.exceptions import
from ukrdc_cupid.core.modify.edit_feed import ukrdcid_split_merge, force_quarantined
from sqlalchemy.orm import Session
from ukrdc_sqla.ukrdc import PatientRecord
from ukrdc_cupid.core.store.exceptions import (
    SchemaVersionError,
    InsertionBlockedError,
)
from ukrdc_cupid.core.audit.domain import generate_domain_match_workitems, generate_domain_data_audit


app = FastAPI()


def get_session() -> Session:
    sessionmaker = UKRDCConnection().create_sessionmaker()
    session = sessionmaker()
    try:
        yield session
    finally:
        session.close()


async def _get_xml_body(request: Request) -> str:
    """
    Based on function lifted from the rda_xml_schema_conversion this lifts
    Returns:
        str: XML string
    """

    try:
        content_type = request.headers.get("Content-Type")
        if content_type and "application/xml" in content_type:
            xml_body = await request.body()
            xml_body_decoded = xml_body.decode("utf-8")
            return xml_body_decoded
        else:
            raise HTTPException(
                status_code=400, detail=f"Content type {content_type} not supported"
            )
    except Exception as e:
        msg = str(e)
        raise HTTPException(
            status_code=400, detail=f"Could not read xml. Failed with error: {msg}"
        )


@app.post("/parse/xml_validate/{schema_version}")
async def validate_xml(schema_version: str, xml_body=Depends(_get_xml_body)):
    """Cupid validation functionality simply checks if an xml file is valid
    against the UKRDC RDA schema. Should this contain an option to list the
    schema versions which are available to validate against?
    """

    try:
        errors = validate_rda_xml_string(
            rda_xml=xml_body, schema_version=schema_version
        )
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=500, detail=f"Validation failed with error: {error_msg}."
        )

    if errors:
        msg = f"XML file not valid against {schema_version} schema.\n"
        msg = msg + "".join(
            [f"Error on {line}. {error}\n" for line, error in errors.items()]
        )
    else:
        msg = f"XML file valid against {schema_version}"

    return Response(content=msg)


@app.post("/store/upload_patient_file/{mode}")
async def load_xml(
    mode: str,
    xml_body: str = Depends(_get_xml_body),
    ukrdc_session_factory: Session = Depends(get_session),
):
    """Main CUPID Api route. Cupid will attempt to load any xml posted here to
    the database.

    Args:
        mode (str): _description_
        xml_body (str, optional): _description_. Defaults to Depends(_get_xml_body).
        ukrdc_session_factory (Session, optional): _description_. Defaults to Depends(get_session).

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """

    with ukrdc_session_factory as session:
        # identify patient
        try:
            msg = process_file(xml_body, session, mode)
        except Exception as e:
            # handle exception based on what it is
            if isinstance(e, SchemaVersionError):
                raise HTTPException(status_code=422, detail=str(e))

            elif isinstance(e, InsertionBlockedError):
                raise HTTPException(status_code=422, detail=str(e))

            else:
                error_msg = str(e)
                raise HTTPException(
                    status_code=500, detail=f"Upload failed with error: {error_msg}"
                )

    return Response(content=msg)


@app.post("/modify/ukrdcid")
async def split_merge_ukrdcid(
    pid: str, ukrdcid: str = None, ukrdc_session: Session = Depends(get_session)
):
    # async def split_merge_ukrdcid(pid: str, ukrdcid: str = None):
    """API route to change the UKRDC ID of a patient feed. Provide ukrdcid to merge
    with existing, otherwise a new ukrdcid will be minted separating the record
    from others with the same id.
    """

    with ukrdc_session as session:
        try:
            ukrdcid_split_merge(session=session, pid=pid, ukrdcid=ukrdcid)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Split/Merge failed with error: {str(e)}"
            )

    return Response(content="UKRDC ID split/merge operation completed successfully")


@app.post("/modify/force_merge_file/{issue_id}/{domain_pid}")
async def force_upload_file(
    issue_id: str, domain_pid: str, ukrdc_session: Session = Depends(get_session)
):
    """API route to reprocess quarantined files

    Args:
        pid (str): _description_
        issue_id (str): _description_
        mode (str): _description_
        ukrdc_session (Session, optional): _description_. Defaults to Depends(get_session).
    """

    if domain_pid == "mint":
        pid = None
    else:
        pid = domain_pid

    try:
        force_quarantined(ukrdc_session, issue_id, pid)
    except Exception as e:
        msg = f"Failed with following error {e}"
        raise HTTPException(status_code=500, detail=msg)

    return Response(content=f"Successfully force merged {issue_id}")


@app.post("/modify/delete_patient/{domain_pid}")
async def delete_patient(
    domain_pid: str, ukrdc_session: Session = Depends(get_session)
):
    """Simply removes patient feed

    Args:
        domain_pid (str): pid of feed to remove
    """

    patient_record = ukrdc_session.get(PatientRecord, domain_pid)
    pid = patient_record.pid
    ukrdcid = patient_record.ukrdcid
    localhosp = patient_record.localpatientid
    ukrdc_session.delete(patient_record)
    ukrdc_session.commit()

    msg = f"Deleted patient with identifiers: pid = {pid}, ukrdcid = {ukrdcid}, localpatientid = {localhosp}"

    return Response(content=msg)


@app.post("/audit/run")
async def run_audit_functions(ukrdc_session: Session = Depends(get_session)):
    """Api route to trigger functions which audit records in the database
    against each other. 
    """
    generate_domain_match_workitems(ukrdc_session)

    generate_domain_data_audit(ukrdc_session)

