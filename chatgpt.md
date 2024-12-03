Project uois is a project based on docker-compose setup.
This contains postgres sql databases as persisten storage for data.
Access to database is controlled by several containers (their names starts with gql_).
Such containers are programed in python with help of sqlalchemy, strawberry aiodataloader libraries.
There is also repository https://github.com/hrbolek/uoishelpers which contains a shared functions and classes for all gql_ containers.
There is one special container named gql_ug which is a bit different. 
The main difference is in authentization.
While other containers use WhoAmIExtension, gql_ug does not.

WhoAmIExtension is extension which query gql_ug at a start of request to get identification of requesting user and retrieving their roles.

All gql_ named containers, including gql_ug container are binded into graphQL federation.
This federation is accessed with apollo_federation container (see https://github.com/hrbolek/apollo_federation).

Input point of whole docker stack is defined with frontend container (see https://github.com/hrbolek/_uois subdirectory server)
This container create a proxy point to uri /api/gql which is for POST verbs posted to apollo_federation.
Container also create a user interface dynamically (see https://github.com/hrbolek/_uois subdirectory server/htmls).

Containers frontend and postgres based cannot be scaled, others can. 
This can help to ballance response.

The python code has a part where are stored table models. 
Usually this is in particular directory in project named srv/DBDefinitions.
The models are defined as classes created with help of sqlalchemy.
While most of them are developed with old sqlalchemy version (1.4), they should be rewritten to version 2.0 and unified to use dataclasses.
To fulfill this request, all table columns must be annotated like

name: Mapped[str] = mapped_column(comment="enity name", defaul=None, nullable=True)

There must be defined BaseModel which is inherited by other models.
Definition of this model must be, it is also and example which defines a response when rewritting is wanted

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

class BaseModel(MappedAsDataclass, DeclarativeBase):
    id: Mapped[uuid.UUID] = UUIDColumn(index=True, primary_key=True, default_factory=uuid.uuid4)

    created: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True, server_default=sqlalchemy.sql.func.now(), comment="date time of creation")
    lastchange: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True, server_default=sqlalchemy.sql.func.now(), comment="date time stamp")

    createdby_id: Mapped[uuid.UUID] = UUIDFKey(ForeignKey("users.id"), comment="id of user who created this entity")
    changedby_id: Mapped[uuid.UUID] = UUIDFKey(ForeignKey("users.id"), comment="id of user who changed this entity")
    rbacobject_id: Mapped[uuid.UUID] = UUIDFKey(comment="id rbacobject")
###

```
Such definition allows to store aditional information for each row in each table in database.
Important goal is to make entities created by sqlalchemy compatible with dataclasses.

To expose table models to graphql endpoint strawberry library is used.

There is BaseGQLModel which is inherited by other graphql models
Its definition must be this, it is also and example which defines a response when rewritting is wanted

```python
import uuid
import datetime
import typing
import strawberry
import dataclasses

from uoishelpers.gqlpermissions import OnlyForAuthentized, RBACObjectGQLModel

IDType = uuid.UUID
UserGQLModel = typing.Annotated["UserGQLModel", strawberry.lazy(".UserGQLModel")]

@classmethod
async def resolve_reference(cls, info: strawberry.types.Info, id: IDType, **otherData):
    _id = IDType(id) if isinstance(id, str) else id
    return None if id is None else cls(id=_id, **otherData)


@strawberry.federation.interface(
    keys=["id"], description="""Entity representing an interface"""
)
class BaseGQLModel:
    
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        raise NotImplementedError()
    
    @classmethod
    def from_dataclass(cls, db_row):
        db_row_dict = dataclasses.asdict(db_row)
        instance = cls(**db_row_dict)
        return instance

    @classmethod
    async def load_with_loader(cls, info: strawberry.types.Info, id: uuid.UUID):
        if id is None: return None

        _id = IDType(id) if isinstance(id, str) else id
        loader = cls.getLoader(info=info)
        db_row = await loader.load(_id)
        
        return None if db_row is None else cls.from_dataclass(db_row=db_row)
    
    @classmethod
    def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID, **otherdata):
        return cls.load_with_loader(info=info, id=id)
       
    id: typing.Optional[IDType] = strawberry.field(
        description="primary key", 
        default=None,
        permission_classes=[OnlyForAuthentized]
        )
    lastchange: typing.Optional[datetime.date] = strawberry.field(
        description="timestamp", 
        default=None,
        permission_classes=[OnlyForAuthentized]
        )
    created: typing.Optional[datetime.date] = strawberry.field(
        description="date & time of unit born", 
        default=None,
        permission_classes=[OnlyForAuthentized]
        )
    createdby_id: typing.Optional[IDType] = strawberry.field(
        description="who created this entity", 
        default=None,
        permission_classes=[OnlyForAuthentized]
        )
    changedby_id: typing.Optional[IDType] = strawberry.field(
        description="who changed this entity", 
        default=None,
        permission_classes=[OnlyForAuthentized]
        )
    rbacobject_id: typing.Optional[IDType] = strawberry.field(
        description="rbac ruling object", 
        default=None,
        permission_classes=[OnlyForAuthentized]
        )

    @strawberry.field(
        description="who created this entity",
        permission_classes=[OnlyForAuthentized]
        )
    async def createdby(self) -> typing.Optional["UserGQLModel"]:
        from .UserGQLModel import UserGQLModel
        return None if self.changedby_id is None else UserGQLModel(id=self.createdby_id)

    @strawberry.field(
        description="who created this entity",
        permission_classes=[OnlyForAuthentized]
        )
    async def changedby(self) -> typing.Optional["UserGQLModel"]:
        from .UserGQLModel import UserGQLModel
        return None if self.changedby_id is None else UserGQLModel(id=self.changedby_id)

    @strawberry.field(
        description="rbac holds relations of user",
        permission_classes=[OnlyForAuthentized]
        )
    async def rbacobject(self) -> typing.Optional["RBACObjectGQLModel"]:
        return None if self.rbacobject_id is None else RBACObjectGQLModel(id=self.rbacobject_id)
```

Other models inherits this one and theirs definition contains fields which are derived from appropriate table model (sqlalchemy based).
An example the table model

```python
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

    group_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=True, default=None, comment="who is responsible for this facility") # UUIDFKey(nullable=True, comment="who is responsible for this facility")#Column(ForeignKey("groups.id"), index=True)
    facilitytype_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilitytypes.id"), index=True, nullable=True, default=None) # Column(ForeignKey("facilitytypes.id"), index=True)
    master_facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), index=True, nullable=True, default=None) # Column(ForeignKey("facilities.id"), index=True, nullable=True)

    @hybrid_property
    def type_id(self):
        return self.facilitytype_id

    masterfacility = relationship("FacilityModel", viewonly=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    subfacilities = relationship ("FacilityModel", remote_side="FacilityModel.id", viewonly=True, uselist=True) # https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    # # https://docs.sqlalchemy.org/en/20/_modules/examples/materialized_paths/materialized_paths.html
    type = relationship("FacilityTypeModel", viewonly=True)#, lazy="joined") # https://docs.sqlalchemy.org/en/20/orm/self_referential.html

```

has own graphql model

```python
import dataclasses
import datetime
import typing
import strawberry

from uoishelpers.gqlpermissions import (
    OnlyForAuthentized,
    SimpleInsertPermission, 
    SimpleUpdatePermission, 
    SimpleDeletePermission
)    
from uoishelpers.resolvers import (
    getLoadersFromInfo, 
    createInputs,

    InsertError, 
    Insert, 
    UpdateError, 
    Update, 
    DeleteError, 
    Delete,

    PageResolver,
    VectorResolver,
    ScalarResolver
)

from .BaseGQLModel import BaseGQLModel, IDType

GroupGQLModel = typing.Annotated["GroupGQLModel", strawberry.lazy(".GroupGQLModel")]
EventGQLModel = typing.Annotated["EventGQLModel", strawberry.lazy(".EventGQLModel")]
FacilityTypeGQLModel = typing.Annotated["FacilityTypeGQLModel", strawberry.lazy(".FacilityTypeGQLModel")]
FacilityEventStateTypeGQLModel = typing.Annotated["FacilityEventStateTypeGQLModel", strawberry.lazy(".FacilityEventStateTypeGQLModel")]
FacilityEventGQLModel = typing.Annotated["FacilityEventGQLModel", strawberry.lazy(".FacilityEventGQLModel")]

# region FacilityGQLModel
@strawberry.federation.type(
    keys=["id"], description="""Entity representing a Facility"""
)
class FacilityGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).FacilityModel
 
    name: typing.Optional[str] = strawberry.field(
        default=None,
        description="""Facility name assigned by an administrator""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    
    name_en: typing.Optional[str] = strawberry.field(
        default=None,
        description="""Facility eng name assigned by an administrator""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
        
    label: typing.Optional[str] = strawberry.field(
        default=None,
        description="""Facility full name assigned by an administrator""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )

    startdate: typing.Optional[datetime.datetime] = strawberry.field(
        default=None,
        description="""Facility datetime """,
        permission_classes=[
            OnlyForAuthentized
        ]
        )

    enddate: typing.Optional[datetime.datetime] = strawberry.field(
        default=None,
        description="""Facility datetime """,
        permission_classes=[
            OnlyForAuthentized
        ]
        )

    # address
    address: typing.Optional[str] = strawberry.field(
        default=None,
        description="""Facility address""",
        permission_classes=[
            OnlyForAuthentized
        ]
    )
    # valid
    valid: typing.Optional[bool] = strawberry.field(
        default=None,
        description="""is the facility still valid""",
        permission_classes=[
            OnlyForAuthentized
            ]
    )

    capacity: typing.Optional[int] = strawberry.field(
        default=None,
        description="""Facility's capacity""",
        permission_classes=[
            OnlyForAuthentized
            ]
    )

    # manager_id

    # address
    geometry: typing.Optional[str] = strawberry.field(
        default=None,
        description="""Facility geometry (SVG)""",
        permission_classes=[
            OnlyForAuthentized
            ]
    )

    geolocation: typing.Optional[str] = strawberry.field(
        default=None,
        description="""Facility geo address (WGS84+zoom)""",
        permission_classes=[
            OnlyForAuthentized
            ]
    )

    group_id: typing.Optional[IDType] = strawberry.field(
        default=None,
        description="""Facility geo address (WGS84+zoom)""",
        permission_classes=[
            OnlyForAuthentized
            ]
    )

    facilitytype_id: typing.Optional[IDType] = strawberry.field(
        default=None,
        description="""Facility geo address (WGS84+zoom)""",
        permission_classes=[
            OnlyForAuthentized
            ]
    )

    master_facility_id: typing.Optional[IDType] = strawberry.field(
        default=None,
        description="""Facility geo address (WGS84+zoom)""",
        permission_classes=[
            OnlyForAuthentized
            ]
    )

    type: typing.Optional["FacilityTypeGQLModel"] = strawberry.field(
        description="""Facility type""",
        permission_classes=[
            OnlyForAuthentized
            ],
        resolver=ScalarResolver["FacilityTypeGQLModel"](fkey_field_name="facilitytype_id")
    )

    master_facility: typing.Optional["FacilityGQLModel"] = strawberry.field(
        description="""Facility above this""",
        permission_classes=[
            OnlyForAuthentized
        ],
        resolver=ScalarResolver["FacilityGQLModel"](fkey_field_name="master_facility_id")
    )

    sub_facilities: typing.List["FacilityGQLModel"] = strawberry.field(
        description="""Facilities inside facility (like buildings in an areal)""",
        permission_classes=[
            OnlyForAuthentized
            ],
        resolver=VectorResolver["FacilityGQLModel"](fkey_field_name="master_facility_id", whereType=)
    )

    group: typing.Optional["GroupGQLModel"] =strawberry.field(
        description="""Facility management group""",
        permission_classes=[
            OnlyForAuthentized
            ],
        resolver=ScalarResolver["GroupGQLModel"](fkey_field_name="group_id")
    )
```

