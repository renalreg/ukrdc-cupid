""" This module should do the job of the merge functionality in the data repository:
https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#L235

or any improvements and updates to the specs. At this point I am thinking it should take sqla objects as inputs 
this makes it as generic as possible. For example if at some point in the future we are doing one of our internal
processes which produces RDA xml we could just call this process directly and pass the sqla models.  

In the original code there is the different storage steps depend on each other (I think). However I think it is better 
that at this point the dependancy structure has been flattened out and each sqla object is self contained. This might 
require some thought as the code currently (incorrectly) plays tricks like using the patient_record start_date: 
https://github.com/renalreg/Data-Repository/blob/52178acad21507678e19c577764f64318aeef896/src/main/java/org/ukrdc/repository/RepositoryManager.java#L339
when deciding which lab orders to delete.

There seems to be a few possible storage modes: 
1) delete everything (within a range for that pid) insert new items to replace them
2) delete any record that has changed and insert replacement for that specific record create any new record 
3) insert any non existing records i.e if id/pid doesn't exist (not sure if there are examples of this)

"""
import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from typing import List


def store_generic(
    orm_objects: List[sqla.Base],  # type:ignore
    session: Session,
    store_mode: str,
):
    """
    Args:
        patient_record_orm (sqla.PatientRecord):
        store_type (str): should the record be overwritten, written if changed or new, only written if new.

    Lots of the tables missing their own storage step think this is handled here in the java code:
    https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#L279

    """
    for object in orm_objects:
        "if logic and store operation"


def store_patient_record(
    patient_records: List[sqla.PatientRecord], session: Session, store_mode: str
):
    """Function to store patient record.

    Args:
        patient_record_orm (sqla.PatientRecord):
        store_type (str): should the record be overwritten, written if changed or new, only written if new.
    """
    pass


def store_patient(patients: List[sqla.Patient], session: Session, store_mode: str):
    """

    Args:
        patient_orm (sqla.Patient): _description_
        store_mode (str): _description_
    """


def store_family_doctor(
    family_doctors: List[sqla.Patient], session: Session, store_mode: str
):
    """_summary_

    Args:
        patient_orm (List[sqla.Patient]): _description_
        session (Session): _description_
        store_mode (str): _description_
    """


def store_pv_data(pv_data: List[sqla.PVData], session: Session, store_mode: str):
    """_summary_

    Args:
        pv_data (List[sqla.PVData]): _description_
        session (Session): _description_
        store_mode (str): _description_
    """


def store_renal_diagnosis(
    renal_diagnosis: List[sqla.RenalDiagnosis], session: Session, store_mode: str
):
    """_summary_

    Args:
        renal_diagnosis (List[sqla.RenalDiagnosis]): _description_
        session (Session): _description_
        store_mode (str): _description_
    """


def store_cause_of_death(
    cause_of_death: List[sqla.CauseOfDeath], session: Session, store_mode: str
):
    """_summary_

    Args:
        cause_of_death (List[sqla.CauseOfDeath]): _description_
        session (Session): _description_
        store_mode (str): _description_
    """


def store_surveys(surveys: List[sqla.Survey], session: Session, store_mode: str):
    """_summary_

    Args:
        survey (List[sqla.Survey]): _description_
        session (Session): _description_
        store_mode (str): _description_
    """


def store_lab_orders(lab_orders: List[sqla.Survey], session: Session, store_mode: str):
    """_summary_

    Args:
        lab_orders (List[sqla.Survey]): _description_
        session (Session): _description_
        store_mode (str): _description_
    """


def store_observations(
    observations: List[sqla.Observation], session: Session, store_mode: str
):
    """_summary_

    Args:
        observations (List[sqla.Observation]): _description_
        session (Session): _description_
        store_mode (str): _description_
    """


def store_dialysis_sessions(
    dialysis_sessions: List[sqla.DialysisSession], session: Session, store_mode: str
):
    """_summary_

    Args:
        observations (List[sqla.Observation]): _description_
        session (Session): _description_
        store_mode (str): _description_
    """


def store_medications(
    medications: List[sqla.Medication], session: Session, store_mode: str
):
    """_summary_

    Args:
        medications (List[sqla.Medication]): _description_
        session (Session): _description_
        store_mode (str): _description_
    """


# def store_documents(medications:List[sqla.Medication], session:Session, store_mode:str)
