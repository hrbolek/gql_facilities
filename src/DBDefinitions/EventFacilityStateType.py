from sqlalchemy import (
    Column,
    String,    
)
from sqlalchemy.orm import Mapped, mapped_column
from .BaseModel import BaseModel

class EventFacilityStateType(BaseModel):
    __tablename__ = "facilityeventstatetypes"

    name: Mapped[str] = mapped_column(default=None, nullable=True) # Column(String)
    name_en: Mapped[str] = mapped_column(default=None, nullable=True) # Column(String)

    # rozvrh, naplánováno, žádost, schváleno, zrušeno, ...
    # planned, requested, accepted, canceled, priority0, priority1, ...

