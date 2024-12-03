import asyncio
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

    @strawberry.field(
            description="""Intermediate entity linking the event and facility""",
            permission_classes=[OnlyForAuthentized]
            )
    async def reservations(self, info: strawberry.types.Info) -> typing.List["FacilityEventGQLModel"]:
        from .FacilityEventGQLModel import FacilityEventGQLModel
        loader = FacilityEventGQLModel.getLoader(info)
        # loader = getLoadersFromInfo(info=info).facilities_events
        # id = resolve_field(self=self, field_name="id")
        id = self.id
        rows = await loader.filter_by(facility_id=id)
        results = (FacilityEventGQLModel.from_dataclass(row) for row in rows)
        # results = await asyncio.gather(*futures)
        return results


@strawberry.field(
        description="""Finds an facility their id""",
        permission_classes=[OnlyForAuthentized]
        )
async def facility_by_id(
    self, info: strawberry.types.Info, id: IDType
) -> typing.Union[FacilityGQLModel, None]:
    result = await FacilityGQLModel.resolve_reference(info=info, id=id)
    return result

@createInputs
@dataclasses.dataclass
class FacilityInputFilter:
    name: str
    name_en: str
    valid: bool
    label: str
    capacity: int
    group_id: IDType
    master_facility_id: IDType
    facilitytype_id: IDType

from uoishelpers.resolvers import PageResolver
    
facility_page = strawberry.field(
        description="""Finds paged facilities""",
        permission_classes=[OnlyForAuthentized],
        resolver=PageResolver[FacilityGQLModel](whereType=FacilityInputFilter)
        )    

# region Facility
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

@strawberry.input(description="attributes needed for operation delete")
class FacilityDeleteGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp")
    id: IDType = strawberry.field(description="primary key")

@strawberry.mutation(
        description="Updates the facility",
        permission_classes=[
            OnlyForAuthentized,
            SimpleUpdatePermission[FacilityGQLModel](roles=["administrátor", "administrátor budov"])
        ]
    )
async def facility_update(self, info: strawberry.types.Info, facility: typing.Annotated[FacilityUpdateGQLModel, strawberry.argument(description="desc")]) -> typing.Union[FacilityGQLModel, UpdateError[FacilityGQLModel]]:
    return await Update[FacilityGQLModel].DoItSafeWay(info=info, entity=facility)

@strawberry.mutation(
        description="Creates a facility, available only for admins",
        permission_classes=[
            OnlyForAuthentized,
            SimpleInsertPermission[FacilityGQLModel](roles=["administrátor", "administrátor budov"])
        ]
    )
async def facility_insert(self, info: strawberry.types.Info, facility: FacilityInsertGQLModel) -> typing.Union[FacilityGQLModel, InsertError[FacilityGQLModel]]:
    # facility.rbacobject_id can be defined from frontend, if not, facility.group_id is used
    # if facility.rbacobject_id == facility.group_id, roles can be checked / derived from assigned group
    facility.rbacobject_id = facility.rbacobject_id if facility.rbacobject_id else facility.group_id
    return await Insert[FacilityGQLModel].DoItSafeWay(info=info, entity=facility)

@strawberry.mutation(
        description="Delete the facility, available only for admins",
        permission_classes=[
            OnlyForAuthentized,
            SimpleDeletePermission[FacilityGQLModel](roles=["administrátor", "administrátor budov"])
        ]
    )
async def facility_delete(self, info: strawberry.types.Info, facility: FacilityDeleteGQLModel) -> typing.Optional[DeleteError[FacilityGQLModel]]:
    return await Delete[FacilityGQLModel].DoItSafeWay(info=info, entity=facility)



# class RBACUpdatePermission(SimpleUpdatePermission):
#     async def has_permission(
#         self, source: typing.Any, info: strawberry.types.Info, **kwargs: typing.Any
#     ) -> typing.Union[bool, typing.Awaitable[bool]]:
#         cls = type(self)
#         loader = cls.getLoader(info=info)
#         first_item = next(iter(kwargs.values()), None)
#         assert first_item is not None, f"item to update is unknown {kwargs}"
#         dbrow = await loader.load(first_item.id)
#         rbacobject_id = getattr(dbrow, "rbacobject_id", None)
#         pass        

# endregion
 