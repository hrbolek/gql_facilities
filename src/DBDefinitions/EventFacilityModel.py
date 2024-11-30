import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .BaseModel import BaseModel, UUIDFKey
class EventFacilityModel(BaseModel):
    __tablename__ = "facilities_events"

    event_id: Mapped[uuid.UUID] = mapped_column(default=None, index=True, nullable=True) #UUIDFKey(nullable=True)#Column(ForeignKey("events.id"), index=True)
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), index=True, default=None)
    state_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilityeventstatetypes.id"), index=True, nullable=True, default=None)

    facility = relationship("FacilityModel", viewonly=True, lazy="joined") # https://docs.sqlalchemy.org/en/20/orm/self_referential.html

