from sqlalchemy.orm import Session
from ukrdc_cupid.core.investigate.models import IssueType, Status, Base
from ukrdc_cupid.core.investigate.picklists import ISSUE_PICKLIST, STATUS_PICKLIST

from typing import List, Type, Any


def update_picklist(
    session: Session, orm_model: Type[Base], picklist: List[List[Any]]
) -> None:
    """
    Updates a generic picklist in the database.

    Args:
        session: session to connect to the ukrdc.
        orm_model: orm model of table with picklists to update.
        picklist: list containing ids and dictionary of attributes
    """
    for item_id, updates in picklist:
        item_orm = session.get(orm_model, item_id)
        if item_orm is not None:
            for key, value in updates.items():
                setattr(item_orm, key, value)
        else:
            item_orm = orm_model(id=item_id, **updates)
            session.add(item_orm)

    session.commit()


def update_picklists(session):
    """Updates the picklists used by the investigations schema

    Args:
        session (_type_): _description_
    """
    update_picklist(session, IssueType, ISSUE_PICKLIST)
    update_picklist(session, Status, STATUS_PICKLIST)
