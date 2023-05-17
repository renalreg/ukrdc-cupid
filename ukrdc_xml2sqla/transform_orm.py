"""Module to transform the orm objects generated from the raw xml. This includes adding: keys, updated on, createdon etc 
"""
from typing import Union
import ukrdc_sqla.ukrdc as orm


def generate_key_resultitem(resultitem: orm.ResultItem, order_id: str, seq_no: int):
    """generates result item key. This is somewhat more complicated than some.
    https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#LL693C5-L693C5

    Args:
        resultitem (orm.ResultItem): _description_
        order_id (str): _description_
        seq_no (int): _description_
    """
    if resultitem.prepost == "PRE":
        prepost = ""
    else:
        prepost = resultitem.prepost

    resultitem.id = f"{order_id}:{prepost}:{resultitem.service_id}:{seq_no}"


def transform_result_item(resultitem: orm.ResultItem, pid: str, order_id: str, seq_no: int):
    """transfroms the result item. This is somewhat more complicated than some.
    https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#LL693C5-L693C5
    TODO: figure out what lastResult variable does
    """
    generate_key_resultitem(resultitem, order_id, seq_no)
    resultitem.pid = pid


def generate_key_laborder(laborder: orm.LabOrder, pid: str):
    # generate lab_order consitant with: https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#L679
    laborder.id = f"{pid}:{laborder.placerid}"


def transform_laborder(laborder: orm.LabOrder, pid: str):
    """transform a list of lab order this function is a port of

    Args:
        laborders (List[orm]): _description_
    """
    generate_key_laborder(laborder, pid)
    laborder.pid = pid
    for seq_no, resultitem in enumerate(laborder.result_items):
        transform_result_item(resultitem, pid, laborder.id, seq_no)


def generate_key_generic(
    orm_object: Union[orm.Name, orm.Address, orm.ContactDetail, orm.PatientNumber, orm.SocialHistory, orm.FamilyHistory, orm.Allergy, orm.Diagnosis],
    pid: str,
    seq_no: int,
):

    """This function generates a generic key for patient record level objects:
    https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#L623
    These are :
    Names
    Addresses
    ContactDetails
    PatientNumbers
    SocialHistories
    FamilyHistories
    Allergies
    Diagnoses
    seq_no may be important
    """
    orm_object.id = f"{pid}:{seq_no}"


def transform_generic_item(
    orm_object: Union[orm.Name, orm.Address, orm.ContactDetail, orm.PatientNumber, orm.SocialHistory, orm.FamilyHistory, orm.Allergy, orm.Diagnosis],
    pid: str,
    seq_no: int,
):
    """Transform a generic top level (patient record) item. Adds pid and key to record.

    Args:
        orm_object (Union[ orm.Name, orm.Address, orm.ContactDetail, orm.PatientNumber, orm.SocialHistory, orm.FamilyHistory, orm.Allergy, orm.Diagnosis ]): _description_
        pid (str): _description_
        seq_no (int): _description_
    """

    generate_key_generic(orm_object, pid, seq_no)
    orm_object.pid = pid
