import datetime
import uuid
from sqlalchemy import (
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

from .BaseModel import BaseModel, UUIDFKey, UUIDColumn
class FacilityModel(BaseModel):
    """Spravuje data spojena s objektem daneho typu"""

    __tablename__ = "facilities"
    # id = UUIDColumn()

    name: Mapped[str] = mapped_column(nullable=True, default=None) # Column(String)
    name_en: Mapped[str] = mapped_column(nullable=True, default=None) # Column(String)
    label: Mapped[str] = mapped_column(nullable=True, default=None, comment="Facility label = name including master facilities like S/1/9") # Column(String, comment="Facility label = name including master facilities like S/1/9")
    address: Mapped[str] = mapped_column(nullable=True, default=None, comment="Real address") # Column(String, comment="Real address")
    valid: Mapped[bool] = mapped_column(nullable=True, default=None, comment="If facility is still available") # Column(Boolean, default=True, comment="If facility is still available")
    startdate: Mapped[datetime.datetime] = mapped_column(nullable=True, default=None, comment="First date of availability") # Column(DateTime, comment="First date of availability")
    enddate: Mapped[datetime.datetime] = mapped_column(nullable=True, default=None, comment="Last date of availability") # Column(DateTime, comment="Last date of availability")
    capacity: Mapped[int] = mapped_column(nullable=True, default=None, comment="How many students") # Column(Integer, comment="How many students")
    geometry: Mapped[str] = mapped_column(nullable=True, default=None, comment="SVG overlay for leaflet") # Column(String, comment="SVG overlay for leaflet")
    geolocation: Mapped[str] = mapped_column(nullable=True, default=None, comment="WGSX;WGSY;Zoom") # Column(String, comment="WGSX;WGSY;Zoom")

    group_id: Mapped[uuid.UUID] = UUIDFKey(ForeignKey("group.id"), index=True, nullable=True, default=None, comment="who is responsible for this facility") # UUIDFKey(nullable=True, comment="who is responsible for this facility")#Column(ForeignKey("groups.id"), index=True)
    facilitytype_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilitytypes.id"), index=True, nullable=True, default=None) # Column(ForeignKey("facilitytypes.id"), index=True)
    master_facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), index=True, nullable=True, default=None) # Column(ForeignKey("facilities.id"), index=True, nullable=True)

    @hybrid_property
    def type_id(self):
        return self.facilitytype_id

    masterfacility = relationship("FacilityModel", viewonly=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    subfacilities = relationship ("FacilityModel", remote_side="FacilityModel.id", viewonly=True, uselist=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    # # https://docs.sqlalchemy.org/en/20/_modules/examples/materialized_paths/materialized_paths.html
    type = relationship("FacilityTypeModel", viewonly=True)#, lazy="joined") # https://docs.sqlalchemy.org/en/20/orm/self_referential.html

