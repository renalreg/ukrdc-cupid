from ukrdc_cupid.core.store.keygen import mint_new_pid, mint_new_ukrdcid

from sqlalchemy.orm import Session
from ukrdc_cupid.core.match.identify import identify_patient_feed, read_patient_metadata, identify_across_ukrdc
from ukrdc_cupid.core.store.insert import insert_incoming_data
from ukrdc_cupid.core.investigate.create_investigation import get_patients
from ukrdc_xsdata.ukrdc import PatientRecord

def process_file(xml_object:PatientRecord, session:Session):
    """The code for the api will look very similar to this I think. 
    until that is written it will have to sit in the utilities.

    Args:
        xml_object (PatientRecord): _description_
        session (Session): _description_

    Returns:
        _type_: _description_
    """
    
    # Attempt to identify patient on same feed
    patient_info = read_patient_metadata(xml_object)
    pid, ukrdcid, investigation = identify_patient_feed(session=session, patient_info=patient_info)

    # Investigations cause file to be diverted
    if investigation:
        return investigation

    # After this point files will be inserted into ukrdc        
    # Mint a pid if we don't have one
    if not pid: 
        pid = mint_new_pid(session=session)
        # Attempt to identify patient across the ukrdc
        ukrdcid, investigation = identify_across_ukrdc(session, patient_info)
        is_new = True # need to revisit whether this is nessary
    else:
        is_new = False
        

    # mint new ukrdcid
    if not ukrdcid:
        ukrdcid = mint_new_ukrdcid(session=session)

    # insert data
    insert_incoming_data(
        ukrdc_session=session, 
        pid=pid, 
        ukrdcid=ukrdcid, 
        incoming_xml_file=xml_object,
        is_new = is_new,  
        debug = True
    )

    if investigation:
        # if there is an investigation raised we will have minted a new ukrdcid
        # this needs to be attached to the issue so it can be resolved
        patient = get_patients((pid,ukrdcid))
        investigation.append_patients(patient)