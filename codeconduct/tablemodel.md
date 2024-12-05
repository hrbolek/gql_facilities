
## Rules
- table or db model is always created with help of sqlalchemy, version 2
- naming convention od class is:
    1. Name always starts with capital letter
    2. Name ends with word "Model"
    3. Name is in singular form
- each model must contain an attribute "__tablename__" which value is name of table in database and is in lower letters, always in plural form
- the model is inherited from BaseModel, which introduces a base set of attributes, see "Definition of BaseModel" part of this file
- all fields are annotated and their value is set to call of mapped_column function
- there can be exception that some fields can use instead of mapped_column the function UUIDFKey, which has same signature
- all fields calls mapped_column, or UUIDFKey, with parameters, nullable=True, default=None, try to add comment
- foreign key name ends with "_id" first part of whole name is in singular form and determine entity name
- if in code is relationship, keep it untouched
- there are fields defined in BaseModel and that fields is not present in other models as they are inherited from BaseModel

## Definition of BaseModel
```python
import uuid
import sqlalchemy
import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass, Mapped, mapped_column

def UUIDFKey(ForeignKeyArg=None, **kwargs):
    newkwargs = {
        **kwargs,
        "index": True, 
        "primary_key": False, 
        "default": None,
        "nullable": True,
        "comment": "foreign key"
    }
    return mapped_column(**newkwargs)

def UUIDColumn(**kwargs):
    newkwargs = {
        **kwargs,
        "index": True, 
        "primary_key": True, 
        "default_factory": uuid.uuid4, 
        "comment": "primary key"
    }
    return mapped_column(**newkwargs)

###########################################################################################################################
#
# zde definujte sve SQLAlchemy modely
# je-li treba, muzete definovat modely obsahujici jen id polozku, na ktere se budete odkazovat
#


class BaseModel(MappedAsDataclass, DeclarativeBase):
    id: Mapped[uuid.UUID] = UUIDColumn(index=True, primary_key=True, default_factory=uuid.uuid4)

    created: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True, server_default=sqlalchemy.sql.func.now(), comment="date time of creation")
    lastchange: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True, server_default=sqlalchemy.sql.func.now(), comment="date time stamp")

    createdby_id: Mapped[uuid.UUID] = UUIDFKey(ForeignKey("users.id"), comment="id of user who created this entity")
    changedby_id: Mapped[uuid.UUID] = UUIDFKey(ForeignKey("users.id"), comment="id of user who changed this entity")
    rbacobject_id: Mapped[uuid.UUID] = UUIDFKey(comment="id rbacobject")
###

```

## Example of response to commands like rewrite or generate

```python
import datetime
import uuid
from sqlalchemy import (
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

from .BaseModel import BaseModel, UUIDFKey
class FacilityModel(BaseModel):
    """Spravuje data spojena s objektem daneho typu"""

    __tablename__ = "facilities"

    name: Mapped[str] = mapped_column(nullable=True, default=None)
    name_en: Mapped[str] = mapped_column(nullable=True, default=None)
    label: Mapped[str] = mapped_column(nullable=True, default=None, comment="Facility label = name including master facilities like S/1/9")
    address: Mapped[str] = mapped_column(nullable=True, default=None, comment="Real address")
    valid: Mapped[bool] = mapped_column(nullable=True, default=None, comment="If facility is still available")
    startdate: Mapped[datetime.datetime] = mapped_column(nullable=True, default=None, comment="First date of availability")
    enddate: Mapped[datetime.datetime] = mapped_column(nullable=True, default=None, comment="Last date of availability")
    capacity: Mapped[int] = mapped_column(nullable=True, default=None, comment="How many students")
    geometry: Mapped[str] = mapped_column(nullable=True, default=None, comment="SVG overlay for leaflet")
    geolocation: Mapped[str] = mapped_column(nullable=True, default=None, comment="WGSX;WGSY;Zoom")

    group_id: Mapped[uuid.UUID] = UUIDFKey(ForeignKey("group.id"), index=True, nullable=True, default=None, comment="who is responsible for this facility")
    facilitytype_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilitytypes.id"), index=True, nullable=True, default=None)
    master_facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), index=True, nullable=True, default=None)

    @hybrid_property
    def type_id(self):
        return self.facilitytype_id

    masterfacility = relationship("FacilityModel", viewonly=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    subfacilities = relationship ("FacilityModel", remote_side="FacilityModel.id", viewonly=True, uselist=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    # # https://docs.sqlalchemy.org/en/20/_modules/examples/materialized_paths/materialized_paths.html
    type = relationship("FacilityTypeModel", viewonly=True)#, lazy="joined") # https://docs.sqlalchemy.org/en/20/orm/self_referential.html

```