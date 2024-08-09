from ukrdc_cupid.core.store.keygen import mint_new_pid

from fastapi import Depends, FastAPI, Request, HTTPException, Response
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string
from ukrdc_cupid.core.utils import UKRDCConnection
from ukrdc_cupid.core.parse.utils import load_xml_from_str
from ukrdc_cupid.core.parse.xml_validate import SUPPORTED_VERSIONS
from ukrdc_cupid.core.match.identify import (
    identify_patient_feed,
    read_patient_metadata,
    identify_across_ukrdc,
)
from ukrdc_cupid.core.store.insert import insert_incoming_data
from ukrdc_cupid.core.modify.id_update import ukrdcid_split_merge
from ukrdc_cupid.core.investigate.create_investigation import get_patients

from sqlalchemy.orm import Session

app = FastAPI()

CURRENT_SCHEMA = max(SUPPORTED_VERSIONS)


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
    against the UKRDC RDA schema
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


@app.post("/store/upload_patient/{mode}")
async def load_xml(
    mode: str,
    xml_body: str = Depends(_get_xml_body),
    ukrdc_session: Session = Depends(get_session),
):
    # async def load_xml(mode: str, xml_body: str = Depends(_get_xml_body)):
    # Load XML and check it
    xml_object, xml_version = load_xml_from_str(xml_body)
    if xml_version < CURRENT_SCHEMA:
        raise HTTPException(
            status_code=422,
            detail=f"XML request on version {xml_version} but cupid requires version {CURRENT_SCHEMA}",
        )

    with ukrdc_session as session:
        # identify patient
        patient_info = read_patient_metadata(xml_object)
        pid, ukrdcid, investigation = identify_patient_feed(
            ukrdc_session=session,
            patient_info=patient_info,
        )

        # if an investigation has been raised in identifying the patient we do not insert
        # (we could introduce a force mode to make it try regardless)
        if investigation:
            investigation.create_issue()
            investigation.append_extras(xml=xml_body, metadata=patient_info)

            raise HTTPException(
                status_code=422, content="Something something issue id..."
            )

        # generate new patient ids if required
        if not pid:
            pid = mint_new_pid(session=session)
            # Attempt to identify patient across the ukrdc
            ukrdcid, investigation = identify_across_ukrdc(
                ukrdc_session=session,
                patient_info=patient_info,
            )
            is_new = True
        else:
            # look up pid against investigations

            is_new = False

        # insert into the database
        insert_incoming_data(
            ukrdc_session=session,
            pid=pid,
            ukrdcid=ukrdcid,
            incoming_xml_file=xml_object,
            is_new=is_new,
            debug=True,
        )

        # Any investigation at this point will be associated with a merge to
        # a single patient record therefore there will be a single pid and
        # ukrdc id associated with it. Are we potentially storing data that
        # cause problems if the record gets anonomised?
        if investigation:
            # should this be an inbuilt method?
            patient = get_patients((pid, ukrdcid))  # type : ignore
            investigation.append_patients(patient)
            msg = "Successfully uploaded file with investigation raised"
        else:
            msg = "File uploaded"

    return Response(content=msg)


@app.post("/split_merge/ukrdcid")
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

    return {"message": "UKRDC ID split/merge operation completed successfully"}
