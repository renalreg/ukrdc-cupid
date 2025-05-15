from typing import Any


def cull_singlet_lists(my_thing: Any):
    """For some strange reason the xsdata heiarchy randomly has lists appearing
    This utility gets rid of them. Numpy squeeze adjacent.

    Args:
        items (_type_): _description_
    """

    if isinstance(my_thing, list):
        if len(my_thing) == 0:
            return None
        elif len(my_thing) == 1:
            return my_thing[0]
        else:
            raise Exception("Trying to remove list which isn't singlet")
    else:
        return my_thing
