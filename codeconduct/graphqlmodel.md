## Rules
- graphgl model is createed with help of strawberry library
- naming convetion of model class is:
    1. Name always starts with capital letter
    2. Name ends with word "GQLModel"
    3. If the name has multiple words CamelCase convetion is used
- example of such model is introduced in part "Example of GQLModel"
- fields are derived from table model, details about that model are described in file "tablemodel.md"
- fields can have type which is in table model annotated, that fields have elemental type and such type can be directly used for definition of graphql model field
- fields which have relationship are defined with:
    1. class named ScalarResolver if the table model has appropriate foreign key, such field is decorated "typing.Optional"
    2. class named VectorResolver if the table model has no appropriate foreign key, such field is decorated "typing.List"
- there are other classes with special purpose
    1. class which name ends with InputFilter, example of this class is introduced in part "Example of InputFilter" of this file
    2. classes for insert operation, its name ends with InsertGQLModel example of such class with its use in mutation is introduced in part "Example of InsertGQLModel" of this file, this class have field id which allows to create primary key on client. Field id is optional.
    3. classes for update operation, its name ends with UpdateGQLModel example of such class with its use in mutation is introduced in part "Example of UpdateGQLModel" of this file
    4. classes for delete operation, its name ends with DeleteGQLModel example of such class with its use in mutation is introduced in part "Example of DeleteGQLModel" of this file

- there are also standalone strawberry fields which are used as fields of Query graphQL model which is root of all queries.
    - _by_id is field for retrieval of single entity, this must be queried with parameter id
    - _page is field for retrieval of list of entities, it is possible query with where parameter which define filter, see "InputFilter", also skip and limit parameters can be used to access particular part of returned list

## Example of GQLModel
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
        resolver=VectorResolver["FacilityGQLModel"](fkey_field_name="master_facility_id", whereType=None)
    )

    group: typing.Optional["GroupGQLModel"] =strawberry.field(
        description="""Facility management group""",
        permission_classes=[
            OnlyForAuthentized
            ],
        resolver=ScalarResolver["GroupGQLModel"](fkey_field_name="group_id")
    )

```

## Example of InputFilter
```python
@createInputs
@dataclasses.dataclass
class FacilityInputFilter:
    name: str
    name_en: str
    valid: bool
    label: str
    geometry: str
    geolocation: str
    capacity: int
    group_id: IDType
    master_facility_id: IDType
    facilitytype_id: IDType
```

## Example of InsertGQLModel
```python
@strawberry.input(description="initial attributes for facility insert")
class FacilityInsertGQLModel:
    name: str = strawberry.field(description="name of the new facility")
    facilitytype_id: typing.Optional[IDType] = strawberry.field(description="facility type", default=None)
    id: typing.Optional[IDType] = strawberry.field(description="primary key (UUID), could be client generated", default=None)

    name_en: typing.Optional[str] = strawberry.field(description="english name of facility", default="")
    label: typing.Optional[str] = strawberry.field(description="full name (including masterfacility)", default="")
    address: typing.Optional[str] = strawberry.field(description="postal address", default="")
    valid: typing.Optional[bool] = strawberry.field(description="if facility exists", default=True)
    capacity: typing.Optional[int] = strawberry.field(description="facility capacity", default=0)
    geometry: typing.Optional[str] = strawberry.field(description="SVG overlay for leaflet", default="")
    geolocation: typing.Optional[str] = strawberry.field(description="WSGBLX;WGSBLY;ZOOM", default="")

    group_id: typing.Optional[IDType] = strawberry.field(description="group which is responsible for management of this facility", default=None)
    master_facility_id: typing.Optional[IDType] = strawberry.field(description="to which facility this facility belongs", default=None)
    rbacobject_id: typing.Optional[IDType] = \
        strawberry.field(description="group_id or user_id defines access rights", default=None)
    createdby_id: strawberry.Private[IDType] = None


@strawberry.mutation(
        description="Creates a facility, available only for admins",
        permission_classes=[
            OnlyForAuthentized,
            SimpleInsertPermission[FacilityGQLModel](roles=["administrátor", "administrátor budov"])
        ]
    )
async def facility_insert(self, info: strawberry.types.Info, facility: FacilityInsertGQLModel) -> typing.Union[FacilityGQLModel, InsertError[FacilityGQLModel]]:
    facility.rbacobject_id = facility.rbacobject_id if facility.rbacobject_id else facility.group_id
    return await Insert[FacilityGQLModel].DoItSafeWay(info=info, entity=facility)

```

## Example of UpdateGQLModel
```python
@strawberry.input(description="set of updateable attributes")
class FacilityUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp")
    id: IDType = strawberry.field(description="primary key")

    name: typing.Optional[str] = strawberry.field(description="name of the new facility", default=None)
    facilitytype_id: typing.Optional[IDType] = strawberry.field(description="facility type", default=None)

    name_en: typing.Optional[str] = strawberry.field(description="english name of facility", default=None)
    label: typing.Optional[str] = strawberry.field(description="full name (including masterfacility)", default=None)
    address: typing.Optional[str] = strawberry.field(description="postal address", default=None)
    valid: typing.Optional[bool] = strawberry.field(description="if facility exists", default=None)
    capacity: typing.Optional[int] = strawberry.field(description="facility capacity", default=None)
    geometry: typing.Optional[str] = strawberry.field(description="SVG overlay for leaflet", default=None)
    geolocation: typing.Optional[str] = strawberry.field(description="WSGBLX;WGSBLY;ZOOM", default=None)

    group_id: typing.Optional[IDType] = strawberry.field(description="group which is responsible for management of this facility", default=None)
    master_facility_id: typing.Optional[IDType] = strawberry.field(description="to which facility this facility belongs", default=None)
    changedby_id: strawberry.Private[IDType] = None

@strawberry.mutation(
        description="Updates the facility",
        permission_classes=[
            OnlyForAuthentized,
            SimpleUpdatePermission[FacilityGQLModel](roles=["administrátor", "administrátor budov"])
        ]
    )
async def facility_update(self, info: strawberry.types.Info, facility: typing.Annotated[FacilityUpdateGQLModel, strawberry.argument(description="desc")]) -> typing.Union[FacilityGQLModel, UpdateError[FacilityGQLModel]]:
    return await Update[FacilityGQLModel].DoItSafeWay(info=info, entity=facility)    
```

## Example of DeleteGQLModel
```python
@strawberry.input(description="set of updateable attributes")
class FacilityDeleteGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp")
    id: IDType = strawberry.field(description="primary key")

@strawberry.mutation(
        description="Delete the facility, available only for admins",
        permission_classes=[
            OnlyForAuthentized,
            SimpleDeletePermission[FacilityGQLModel](roles=["administrátor", "administrátor budov"])
        ]
    )
async def facility_delete(self, info: strawberry.types.Info, facility: FacilityDeleteGQLModel) -> typing.Optional[DeleteError[FacilityGQLModel]]:
    return await Delete[FacilityGQLModel].DoItSafeWay(info=info, entity=facility)

```