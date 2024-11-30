import dataclasses
import typing
import datetime
import strawberry

import strawberry.types
from uoishelpers.resolvers import getLoadersFromInfo, createInputs
from uoishelpers.gqlpermissions import (
    OnlyForAuthentized,
    SimpleInsertPermission, 
    SimpleUpdatePermission, 
    SimpleDeletePermission
)    
from uoishelpers.resolvers import (
    InsertError, 
    Insert, 
    UpdateError, 
    Update, 
    DeleteError, 
    Delete
)
from uoishelpers.resolvers import PageResolver

from .BaseGQLModel import BaseGQLModel, IDType

# region FacilityTypeGQLModel

@strawberry.federation.type(
    keys=["id"], description="""Entity representing a facility type"""
)
class FacilityTypeGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).facilitytypes

    name: typing.Optional[str] = strawberry.field(
        description="""Facility name assigned by an administrator""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    
    name_en: typing.Optional[str] = strawberry.field(
        description="""Facility eng name assigned by an administrator""",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
# endregion

# region FacilityType
@strawberry.field(
        description="""Finds an facility type by its id""",
        permission_classes=[OnlyForAuthentized]
        )
async def facility_type_by_id(
    self, info: strawberry.types.Info, id: IDType
) -> typing.Optional[FacilityTypeGQLModel]:
    result = await FacilityTypeGQLModel.resolve_reference(info=info, id=id)
    return result

@createInputs
@dataclasses.dataclass
class FacilityTypeInputFilter:
    name: str
    name_en: str
    id: IDType

facility_type_page = strawberry.field(
        description="""Returns all facility types""",
        permission_classes=[OnlyForAuthentized],
        # graphql_type=typing.List[FacilityTypeGQLModel],
        resolver=PageResolver[FacilityTypeGQLModel](whereType=FacilityTypeInputFilter)
        )
# endregion

# region FacilityType
@strawberry.input(description="First datastructure for Facility type creation")
class FacilityTypeInsertGQLModel:
    name: str = strawberry.field(description="name of Facility type")
    name_en: typing.Optional[str] = strawberry.field(description="english name of Facility type", default=None)
    id: typing.Optional[IDType] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    createdby: strawberry.Private[IDType] = None
    rbacobject_id: typing.Optional[IDType] = \
        strawberry.field(description="group_id or user_id defines access rights", default=None)


@strawberry.input(description="Datastructure for Facility type update")
class FacilityTypeUpdateGQLModel:
    id: IDType = strawberry.field(description="primary key (UUID)")

    lastchange: datetime.datetime = strawberry.field(description="timestamp")
    name: typing.Optional[str] = strawberry.field(description="name of Facility type", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="english name of Facility type", default=None)
    changedby: strawberry.Private[IDType] = None
    rbacobject_id: strawberry.Private[IDType] = None

@strawberry.input(description="Datastructure for Facility type delete operation")
class FacilityTypeDeleteGQLModel:
    id: IDType = strawberry.field(description="primary key (UUID)")

    lastchange: datetime.datetime = strawberry.field(description="timestamp")
   
@strawberry.mutation(
    description="Creates new facility type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[FacilityTypeGQLModel](roles=["administrátor"])
    ])
async def facility_type_insert(self, info: strawberry.types.Info, facility_type: FacilityTypeInsertGQLModel) -> typing.Union[FacilityTypeGQLModel, InsertError[FacilityTypeGQLModel]]:
    return await Insert[FacilityTypeGQLModel].DoItSafeWay(info=info, entity=facility_type)

@strawberry.mutation(
    description="Updates the facility type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[FacilityTypeGQLModel](roles=["administrátor"]),
    ])
async def facility_type_update(self, info: strawberry.types.Info, facility_type: FacilityTypeUpdateGQLModel) -> typing.Union[FacilityTypeGQLModel, UpdateError[FacilityTypeGQLModel]]:
    return await Update[FacilityTypeGQLModel].DoItSafeWay(info=info, entity=facility_type)

@strawberry.mutation(
    description="Deletes the facility type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[FacilityTypeGQLModel](roles=["administrátor"]),
    ])
async def facility_type_delete(self, info: strawberry.types.Info, facility_type: FacilityTypeDeleteGQLModel) -> typing.Optional[DeleteError[FacilityTypeGQLModel]]:
    return await Delete[FacilityTypeGQLModel].DoItSafeWay(info=info, entity=facility_type)

# endregion

