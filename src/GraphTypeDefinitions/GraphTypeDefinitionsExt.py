import strawberry
import dataclasses
import datetime

from typing import List, Optional
from ._GraphResolvers import getLoadersFromInfo, IDType


@classmethod
async def resolve_reference(cls, info: strawberry.types.Info, id: IDType):
    if id is None:
        return None
    _id = IDType(id) if isinstance(id, str) else id
    return cls(id=_id)

# @strawberry.federation.type(extend=True, keys=["id"])
# class UserGQLModel:
#     id: IDType = strawberry.federation.field(external=True)
#     # resolve_reference = resolve_reference
#     resolve_reference


# @strawberry.federation.type(extend=True, keys=["id"])
# class GroupGQLModel:
#     id: IDType = strawberry.federation.field(external=True)
#     resolve_reference = resolve_reference

# @strawberry.federation.type(extend=True, keys=["id"])
# class EventGQLModel:

#     id: IDType = strawberry.federation.field(external=True)
#     resolve_reference = resolve_reference


@strawberry.federation.type(extend=True, keys=["id"])
class RBACObjectGQLModel:
    id: IDType = strawberry.federation.field(external=True)

    @classmethod
    async def resolve_roles(cls, info: strawberry.types.Info, id: IDType):
        loader = getLoadersFromInfo(info).authorizations
        authorizedroles = await loader.load(id)
        return authorizedroles

    @classmethod
    async def resolve_all_roles(cls, info: strawberry.types.Info):
        return []