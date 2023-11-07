import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from datetime import datetime
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.store.delete import SQL_DELETE

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore

from typing import List, Optional, Union


def add_records(
        ukrdc_session: Session, 
        incoming_records = List[sqla.Base], 
    ):
    """This function takes the list of orm objects and adds them to the session. 
    After this they are treated in 3 different catagories.
    unchanged: 

    Args:
        ukrdc_session (Session): _description_
        incoming_records (_type_, optional): _description_. Defaults to List[sqla.Base].
    """

    n_incoming = len(incoming_records)
    print(f"Total of {len(incoming_records)} incoming records")

    # add loaded records to the session
    for record in incoming_records:
        ukrdc_session.merge(record)

    ukrdc_session.flush()
    
    # modify dirty records 
    n_dirty = len(ukrdc_session.dirty)
    print(f"Total of {n_dirty} dirty")
    for record in ukrdc_session.dirty:
        print("set any fields required when a record is updated")

    # modify new records
    n_transient = 0
    n_dirty = 0    
    for record in incoming_records:
        state = inspect(record)
        if state.transient:
            n_transient +=1


    print(f"Total of {n_transient } new")
    print(f"Total of {n_incoming - n_dirty- n_transient} unchanged")


def delete_records(
        ukrdc_session: Session, 
        pid:str,
        incoming_ids : List[str] 
    ):
    print("")

def delete_timebound_records(
        ukrdc_session: Session, 
        pid : str,
        start_time : datetime, 
        stop_time : datetime 
    ):
    print("")


def insert_incoming_data(ukrdc_session: Session, pid:str, ukrdcid:str, incoming_xml_file: xsd_ukrdc.PatientRecord, no_delete:bool = False):
    """Insert file into the database having matched to pid.  

    Args:
        pid (str): _description_
        incoming_xml_file (xsd_ukrdc.PatientRecord): _description_
        no_delete (bool, optional): _description_. Defaults to False.
    """

    # load incoming xml file into cupid store models
    patient_record = PatientRecord(incoming_xml_file)
    patient_record.map_xml_to_tree()

    # transform records in the file to how they will appear in database
    patient_record.transform(pid=pid, ukrdcid=ukrdcid)

    # get records to be inserted in a linear form
    incoming_records = patient_record.get_orm_dict()
    all_incoming_records =  [item for sublist in incoming_records.values() for item in sublist]

    # add records to the session
    add_records(ukrdc_session, all_incoming_records)

    # delete any records we hold which are not in incoming RDA 
    if no_delete is not True:
        for tablename, record in incoming_records.items():
            if tablename in ("laborder", ""):
                print("")
            elif tablename in ("score", ):
                print("")
            else:
                delete_record = SQL_DELETE.get(tablename)
                if delete_record is not None: 
                    delete_records(ukrdc_session, pid, []) 
                #delete_time_bound()
    

    ukrdc_session.commit()