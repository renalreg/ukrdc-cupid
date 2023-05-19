from sqlalchemy.orm import Session
from sqlalchemy import Sequence


def mint_new_pid(session: Session):
    """
    Function to mint new pid. This sequence doesn't currently exist in the ukrdc, create by running script make_pid_generation_sequence.py
    """
    new_pid_seq = Sequence("generate_new_pid")
    new_pid = str(session.execute(new_pid_seq))

    return new_pid
