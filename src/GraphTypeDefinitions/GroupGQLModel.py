import strawberry
from .BaseGQLModel import IDType

@strawberry.federation.type(extend=True, keys=["id"])
class GroupGQLModel:
    id: IDType = strawberry.federation.field(external=True)

    from .BaseGQLModel import resolve_reference
