import typing
import strawberry
import datetime

import strawberry.types
from uoishelpers.resolvers import getLoadersFromInfo

from .BaseGQLModel import BaseGQLModel, IDType
# from .CUD import InsertError, Insert, UpdateError, Update, DeleteError, Delete
from uoishelpers.resolvers import InsertError, Insert, UpdateError, Update, DeleteError, Delete

FacilityGQLModel = typing.Annotated["FacilityGQLModel", strawberry.lazy(".FacilityGQLModel")]   
EventGQLModel = typing.Annotated["EventGQLModel", strawberry.lazy(".EventGQLModel")]   
FacilityEventStateTypeGQLModel = typing.Annotated["FacilityEventStateTypeGQLModel", strawberry.lazy(".FacilityEventStateTypeGQLModel")]   

from uoishelpers.gqlpermissions import (
    OnlyForAuthentized,
)

# region FacilityEventGQLModel
@strawberry.federation.type(
    keys=["id"], description="""Entity representing the link between facility and event"""
)
class FacilityEventGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).EventFacilityModel

    # _data: strawberry.Private[object]

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
            
    #         "event_id": lambda row: row.event_id,
    #         "facility_id": lambda row: row.facility_id,
    #         "state_id": lambda row: row.state_id,
            
    #         "_data": lambda row: row,
    #     }

    event_id: typing.Optional[IDType] = strawberry.field(description="")
    facility_id: typing.Optional[IDType] = strawberry.field(description="")
    state_id: typing.Optional[IDType] = strawberry.field(description="")

    @strawberry.field(
            description="""the event""",
            permission_classes=[
                OnlyForAuthentized
            ]
            )
    async def event(self, info: strawberry.types.Info) -> typing.Optional["EventGQLModel"]:
        from .EventGQLModel import EventGQLModel
        return await EventGQLModel.resolve_reference(info=info, id=self.event_id)

    @strawberry.field(
            description="""the facility""",
            permission_classes=[
                OnlyForAuthentized
            ]
            )
    async def facility(self, info: strawberry.types.Info) -> typing.Optional["FacilityGQLModel"]:
        from .FacilityGQLModel import FacilityGQLModel
        result = await FacilityGQLModel.resolve_reference(info=info, id=self.facility_id)
        return result

    @strawberry.field(
            description="""the facility state (reserved for an event, lesson planned etc.)""",
            permission_classes=[
                OnlyForAuthentized
            ]
            )
    async def state(self, info: strawberry.types.Info) -> typing.Optional["FacilityEventStateTypeGQLModel"]:
        from .FacilityEventStateTypeGQLModel import FacilityEventStateTypeGQLModel
        result = await FacilityEventStateTypeGQLModel.resolve_reference(info=info, id=self.state_id)
        return result

# endregion
 
@strawberry.input(description="Initial data for reservation model")
class FacilityReservationInsertGQLModel:
    id: typing.Optional[IDType]
    facility_id: IDType =  strawberry.field(description="facility for reservation")
    event_id: IDType = strawberry.field(description="event for reservation")
    state_id: IDType = strawberry.field(description="initial state of reservation")
    createdby_id: strawberry.Private[IDType] = None
    rbacobject_id: typing.Optional[IDType] = \
        strawberry.field(description="group_id or user_id defines access rights", default=None)

@strawberry.input(description="Initial data for reservation model")
class FacilityReservationUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime = strawberry.field(description="timestamp")
    state_id: IDType = strawberry.field(description="state of reservation")
    changedby_id: strawberry.Private[IDType] = None
    rbacobject_id: strawberry.Private[IDType] = None

@strawberry.input(description="Initial data for reservation model")
class FacilityReservationDeleteGQLModel:
    id: typing.Optional[IDType]
    lastchange: datetime.datetime = strawberry.field(description="timestamp")

@strawberry.mutation(
        description="Create a facility reservation for a particular event if such reservation exist, UpdateError is returned",
        permission_classes=[
            OnlyForAuthentized
        ]
)
async def facility_reservation_create(self, info: strawberry.types.Info, facility_reservation: FacilityReservationInsertGQLModel) -> typing.Union["FacilityEventGQLModel", InsertError["FacilityEventGQLModel"], UpdateError["FacilityEventGQLModel"]]:
    from .FacilityEventGQLModel import FacilityEventGQLModel
    loader = FacilityEventGQLModel.getLoader(info=info)
    rows = await loader.filter_by(
        event_id=facility_reservation.event_id, 
        facility_id=facility_reservation.facility_id)
    anyrow = next(rows, None)
    if anyrow:
        return UpdateError[FacilityEventGQLModel](msg="reservation already exists", _entity=FacilityEventGQLModel.from_dataclass(anyrow), _input=facility_reservation)
    return await Insert[FacilityEventGQLModel].DoItSafeWay(info=info, entity=facility_reservation)

@strawberry.mutation(
        description="",
        permission_classes=[
            OnlyForAuthentized
        ]
)
async def facility_reservation_update(self, info: strawberry.types.Info, facility_reservation: FacilityReservationUpdateGQLModel) -> typing.Union["FacilityEventGQLModel", UpdateError["FacilityEventGQLModel"]]:
    from .FacilityEventGQLModel import FacilityEventGQLModel
    return await Update[FacilityEventGQLModel].DoItSafeWay(info=info, entity=facility_reservation)


@strawberry.mutation(
        description="",
        permission_classes=[
            OnlyForAuthentized
        ]
)
async def facility_reservation_delete(self, info: strawberry.types.Info, facility_reservation: FacilityReservationDeleteGQLModel) -> typing.Optional[DeleteError["FacilityEventGQLModel"]]:
    from .FacilityEventGQLModel import FacilityEventGQLModel
    return await Delete[FacilityEventGQLModel].DoItSafeWay(info=info, entity=facility_reservation)
