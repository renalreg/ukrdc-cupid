"""Functions to identify items in the dataset already in the ukrdc. 

Returns:
    _type_: _description_
"""

import ukrdc_sqla.ukrdc as orm

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy import select, and_, tuple_
from ukrdc_cupid.core.audit.validate_matches import  validate_demog, validate_demog_ukrdc
from ukrdc_cupid.core.investigate import create_investigation

def match_ni(session: Session, patient_info:dict):
    """This is to handle changes to the MRN. 
    This will need updating to handle sites switching feeds? 

    Args:
        session (Session): _description_
        patient_info (dict): _description_
    """

    # look up pid by trying to match the NI
    pid_query = (
        select(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
        .join(orm.PatientNumber, orm.PatientNumber.pid == orm.PatientRecord.pid)
        .where(
            orm.PatientRecord.sendingextract == patient_info["sending_extract"],
            orm.PatientRecord.sendingfacility == patient_info["sending_facility"],
            orm.PatientNumber.numbertype == "NI",
            and_(
                tuple_(
                    orm.PatientNumber.patientid, 
                    orm.PatientNumber.organization
                ).in_(patient_info["NI"])
            ),
        )
        .group_by(
            orm.PatientRecord.pid, 
            orm.PatientRecord.ukrdcid
        )
    )

    return session.execute(pid_query).fetchall()


def match_mrn(session: Session, patient_info:dict):
    """For the purposes of CUPID the MRN will be the id in the first instance for 
    all 

    Args:
        session (Session): _description_
        patient_info (dict): _description_
    """
    
    # look up pid by trying to match the MRN
    pid_query = (
        select(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
        .join(orm.PatientNumber, orm.PatientNumber.pid == orm.PatientRecord.pid)
        .where(
            orm.PatientRecord.sendingextract == patient_info["sending_extract"],
            orm.PatientRecord.sendingfacility == patient_info["sending_facility"],
            and_(
                orm.PatientNumber.patientid == patient_info["MRN"][0],
                orm.PatientNumber.organization == patient_info["MRN"][1],
                orm.PatientNumber.numbertype == "MRN" 
            ),
        )
        .group_by(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
    )

    return session.execute(pid_query).fetchall()


def read_patient_metadata(xml:xsd_ukrdc.PatientRecord):
    """Function to parse information into an easy to handle format. 
    Will need to handle opt-outs eventually.

    Args:
        xml (xsd_ukrdc.Patient): 
    """

    # we can specify exactly which catagories we want to validate on later 
    patient_info = {
        "sending_extract" : xml.sending_extract.value,
        "sending_facility" : xml.sending_facility.value,
        "date_of_birth" : xml.patient.birth_time.to_datetime(),
        #"gender" : xml.patient.gender,
        #"postcodes" : [address.postcode for address in xml.patient.addresses.address],
        "MRN" : None,
        "NI" : []
    }

    # main matching against pid and ukrdc is done using patient numbers
    for number in xml.patient.patient_numbers[0].patient_number:
        if number.number_type.value == "MRN":
            patient_info["MRN"] = [number.number, number.organization.value]

        if number.number_type.value == "NI":
            patient_info["NI"].append([number.number, number.organization.value]) 

    # MRN is non negotiable for cupid matching
    if not patient_info.get("MRN"):
        raise Exception("placeholder exception...this should really never pass validation")

    return patient_info


def identify_patient_feed(session: Session, patient_info:dict):
    """Identify patient based on patient numbers.

    Args:
        session (Session): SQLAlchemy session
        xml (xsd_ukrdc.PatientRecord): UKRDC patient record as XML
    """

    # match patients on mrn
    matched_patients_mrn = match_mrn(session, patient_info)
    matched_patients_ni = match_ni(session, patient_info)


    # new patient?
    if len(matched_patients_mrn) == 0: 
        if len(matched_patients_ni) == 0:
            return None, None, None
        else: 
            # generate investigation in the end I think these will look more like sqla models
            return None, None, create_investigation.create_ambiguous()

    # unambiguously match to single domain patient?
    if len(matched_patients_mrn) > 1:
        return None, None, create_investigation.create_ambiguous()

    # patient should now be singular
    pid, ukrdcid = matched_patients_mrn[0] 
    
    # validate anonymous patients - bit more thought needed here
    if patient_info["MRN"][1] == "UKRR":
        # validate dob, we use same function but implicitly it is only validating on year of birth
        # I'm assumng these patients wont be sent with NIs
        if validate_demog(session, patient_info["date_of_birth"], pid):
            return pid, ukrdcid,  None
        else:
            return None, None, create_investigation.create_invalid_feed() 
        
    # check NI and MRN give the same story
    # if the NI's match to anything they should be identical to the MRN
    if matched_patients_mrn != matched_patients_ni and len(matched_patients_ni) != 0:
        return None, None, create_investigation.create_ambiguous()
    
    # check dob
    is_valid = validate_demog(session, patient_info["date_of_birth"], pid)
    
    if is_valid:
        return pid, ukrdcid,  None
    else:
        return None, None, create_investigation.create_invalid_feed() 

def match_ukrdc(session: Session, patient_ids:dict):
    
    ukrdc_query = (
        select(orm.PatientRecord.ukrdcid)
        .join(orm.PatientNumber, orm.PatientNumber.pid == orm.PatientRecord.pid)
        .where(
            tuple_(
                orm.PatientNumber.patientid, 
                orm.PatientNumber.organization
            ).in_(patient_ids)
        )
        .group_by(
            orm.PatientRecord.ukrdcid
        )
    )

    return session.execute(ukrdc_query).fetchall()

def identify_across_ukrdc(session: Session, patient_info:dict, pid:str):
    """Since merging and unmerging patients with ukrdc is easier in the case where a problem arises we just create a new patient and load the file.

    Args:
        session (Session): _description_
        patient_info (dict): _description_
    """

    # search for exact match on incoming id
    ids = patient_info["NI"]

    # hopefully where ni is not sufficient MRN should be enough to match something
    if patient_info["MRN"][1] in ["CHI", "HSC", "NHS"]:
        ids = ids + patient_info

    matched_ukrdcids = match_ukrdc(session, ids)

    # handle results of ukrdc matches
    if matched_ukrdcids == 0:
        return None

    elif matched_ukrdcids == 1:
        # verify demgraphics
        ukrdcid = matched_ukrdcids[0]
        is_valid = validate_demog_ukrdc(session, patient_info["date_of_birth"], ukrdcid)
        if is_valid:
            return ukrdcid, None
        else:
            return None, create_investigation.create_invalid_ukrdc(pid) 
    else:
        return None, create_investigation.create_ambiguous_ukrdc(pid) 