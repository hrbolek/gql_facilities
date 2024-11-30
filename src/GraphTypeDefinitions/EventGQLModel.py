import typing
import strawberry
import strawberry.types

from uoishelpers.gqlpermissions import OnlyForAuthentized

from .BaseGQLModel import IDType

FacilityEventGQLModel = typing.Annotated["FacilityEventGQLModel", strawberry.lazy(".FacilityEventGQLModel")]

@strawberry.federation.type(extend=True, keys=["id"])
class EventGQLModel:

    id: IDType = strawberry.federation.field(external=True)

    from .BaseGQLModel import resolve_reference

    @strawberry.field(
        description="reservations for a particular event",
        permission_classes=[
            OnlyForAuthentized
        ]
        )
    async def reservations(self, info: strawberry.types.Info) -> typing.List["FacilityEventGQLModel"]:
        from .FacilityEventGQLModel import FacilityEventGQLModel
        loader = FacilityEventGQLModel.getLoader(info=info)
        rows = await loader.filter_by(event_id=self.id)
        results = (FacilityEventGQLModel.from_dataclass(row) for row in rows)
        return results