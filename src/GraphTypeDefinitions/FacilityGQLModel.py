import asyncio
import dataclasses
import datetime
import typing
import uuid
import strawberry

from sqlalchemy.orm import attributes
from graphql.language import DirectiveLocation
import strawberry.types
from uoishelpers.resolvers import getLoadersFromInfo, createInputs, getUserFromInfo
from uoishelpers.gqlpermissions import (
    OnlyForAuthentized,
    MustBeOneOfPermission
    # OnlyForAdmins
)

from .BaseGQLModel import BaseGQLModel, IDType

OnlyForAdmins = MustBeOneOfPermission("administrátor")

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
    
    # @classmethod
    # def get_table_resolvers(cls):
    #     # raise NotImplementedError()
    #     return {
    #         "id": lambda row: row.id,
    #         "lastchange": lambda row: row.lastchange,
    #         "created": lambda row: row.lastchange,
    #         "createdby_id": lambda row: row.createdby_id,
    #         "changedby_id": lambda row: row.changedby_id,
    #         "rbacobject_id": lambda row: row.rbacobject_id,
    #         "name": lambda row: row.name,
    #         "name_en": lambda row: row.name_en,
    #         "label": lambda row: row.label,
    #         "address": lambda row: row.address,
    #         "valid": lambda row: row.valid,
    #         "capacity": lambda row: row.capacity,
    #         "geometry": lambda row: row.geometry,
    #         "geolocation": lambda row: row.geolocation,
    #         "group_id": lambda row: row.group_id,
    #         "facilitytype_id": lambda row: row.facilitytype_id,
    #         "master_facility_id": lambda row: row.master_facility_id,
            
    #         "_data": lambda row: row,
    #     }

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

    @strawberry.field(
        description="""Facility type""",
        permission_classes=[
            OnlyForAuthentized
            ]
        )
    async def type(self, info: strawberry.types.Info) -> typing.Optional["FacilityTypeGQLModel"]:
        from .FacilityTypeGQLModel import FacilityTypeGQLModel
        result = await FacilityTypeGQLModel.resolve_reference(info=info, id=self.facilitytype_id)
        return result

    @strawberry.field(
            description="""Intermediate entity linking the event and facility""",
            permission_classes=[OnlyForAuthentized]
            )
    async def event_state(self, info: strawberry.types.Info) -> typing.List["FacilityEventStateTypeGQLModel"]:
        from .FacilityEventStateTypeGQLModel import FacilityEventStateTypeGQLModel
        loader = FacilityEventStateTypeGQLModel.getLoader(info)
        loader = getLoadersFromInfo(info=info).facilities_events
        # id = resolve_field(self=self, field_name="id")
        id = self.id
        rows = await loader.filter_by(facility_id=id)
        futures = (FacilityEventStateTypeGQLModel.resolve_reference(info=info, id=row.state_id) for row in rows)
        results = await asyncio.gather(*futures)
        return results

    @strawberry.field(
            description="""Facility above this""",
            permission_classes=[OnlyForAuthentized]
            )
    async def master_facility(self, info: strawberry.types.Info) -> typing.Optional["FacilityGQLModel"]:
        # master_facility_id = resolve_field(self=self, field_name="master_facility_id")
        master_facility_id = self.master_facility_id
        result = await FacilityGQLModel.resolve_reference(info=info, id=master_facility_id)
        return result

    @strawberry.field(
            description="""Facilities inside facility (like buildings in an areal)""",
            permission_classes=[OnlyForAuthentized]
            )
    async def sub_facilities(
        self, info: strawberry.types.Info
    ) -> typing.List["FacilityGQLModel"]:
        loader = FacilityGQLModel.getLoader(info)
        # id = resolve_field(self=self, field_name="id")
        id = self.id
        rows = await loader.filter_by(master_facility_id = id)
        # return result
        futures = (FacilityGQLModel.resolve_reference(info=info, id=row.id) for row in rows)
        result = await asyncio.gather(*futures)
        return result

    @strawberry.field(
            description="""Facility management group""",
            permission_classes=[OnlyForAuthentized]
            )
    async def group(self, info: strawberry.types.Info) -> typing.Optional["GroupGQLModel"]:
        from .GroupGQLModel import GroupGQLModel
        # group_id = resolve_field(self=self, field_name="group_id")
        group_id = self.group_id
        return await GroupGQLModel.resolve_reference(info, id=group_id)
    

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
    createdby_id: typing.Optional[IDType] = strawberry.field(description="who created", default=None)
    rbacobject_id: typing.Optional[IDType] = \
        strawberry.field(description="group_id or user_id defines access rights", default=None)

@strawberry.input(description="set of updateable attributes")
class FacilityUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp")
    id: IDType = strawberry.field(description="primary key")

    name: typing.Optional[str] = strawberry.field(description="name of the new facility", default=None)
    facilitytype_id: typing.Optional[IDType] = strawberry.field(description="facility type", default=None)

    name_en: typing.Optional[str] = strawberry.field(description="english name of facility", default="")
    label: typing.Optional[str] = strawberry.field(description="full name (including masterfacility)", default="")
    address: typing.Optional[str] = strawberry.field(description="postal address", default="")
    valid: typing.Optional[bool] = strawberry.field(description="if facility exists", default=True)
    capacity: typing.Optional[int] = strawberry.field(description="facility capacity", default=0)
    geometry: typing.Optional[str] = strawberry.field(description="SVG overlay for leaflet", default="")
    geolocation: typing.Optional[str] = strawberry.field(description="WSGBLX;WGSBLY;ZOOM", default="")

    group_id: typing.Optional[IDType] = strawberry.field(description="group which is responsible for management of this facility", default=None)
    master_facility_id: typing.Optional[IDType] = strawberry.field(description="to which facility this facility belongs", default=None)
    changed_id: strawberry.Private[IDType] = None

@strawberry.input(description="attributes needed for operation delete")
class FacilityDeleteGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp")
    id: IDType = strawberry.field(description="primary key")

# from .CUD import InsertError, Insert, UpdateError, Update, DeleteError, Delete
from uoishelpers.resolvers import InsertError, Insert, UpdateError, Update, DeleteError, Delete
@strawberry.mutation(
        description="Updates the facility",
        permission_classes=[
            OnlyForAuthentized
        ]
    )
async def facility_update(self, info: strawberry.types.Info, facility: typing.Annotated[FacilityUpdateGQLModel, strawberry.argument(description="desc")]) -> typing.Union[FacilityGQLModel, UpdateError[FacilityGQLModel]]:
    return await Update[FacilityGQLModel].DoItSafeWay(info=info, entity=facility)

@strawberry.mutation(
        description="Creates a facility, available only for admins",
        # permission_classes=[
        #     OnlyForAuthentized,
        #     # OnlyForAdmins
        # ],
        # directives=[RequiresRoleDirective]        
    )
async def facility_insert(self, info: strawberry.types.Info, facility: FacilityInsertGQLModel) -> typing.Union[FacilityGQLModel, InsertError[FacilityGQLModel]]:
    return await Insert[FacilityGQLModel].DoItSafeWay(info=info, entity=facility)

@strawberry.mutation(
        description="Delete the facility, available only for admins",
        permission_classes=[
            OnlyForAuthentized,
            # OnlyForAdmins
        ],
        # directives=[RequiresRoleDirective]
    )
async def facility_delete(self, info: strawberry.types.Info, facility: FacilityDeleteGQLModel) -> typing.Optional[DeleteError[FacilityGQLModel]]:
    return await Delete[FacilityGQLModel].DoItSafeWay(info=info, entity=facility)


# endregion
 