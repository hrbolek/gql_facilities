from sqlalchemy import (
    Column,
    String,
    
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .BaseModel import BaseModel, UUIDFKey
class FacilityTypeModel(BaseModel):
    """Urcuje typ objektu (areal, budova, patro, mistnost)"""

    __tablename__ = "facilitytypes"
    name: Mapped[str] = mapped_column(default=None, nullable=True) # Column(String)
    name_en: Mapped[str] = mapped_column(default=None, nullable=True) # Column(String)
    # name: Mapped[str]
    # name_en: Mapped[str]

    #facilities = relationship("FacilityModel", back_populates="facilitytype")

ft = FacilityTypeModel(name="f", name_en="d")
