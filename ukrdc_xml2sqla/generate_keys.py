def generate_key_laborder(laborder, pid: str):
    # generate lab_order consitant with: https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#L679
    return f"{pid}:{laborder.placerid}"


def generate_key_resultitem(resultitem, order_id: str, seq_no: int):
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

    return f"{order_id}:{prepost}:{resultitem.service_id}:{seq_no}"
