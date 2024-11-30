import typing
import strawberry

from uoishelpers.resolvers import getLoadersFromInfo
from .BaseGQLModel import BaseGQLModel, IDType, OnlyForAuthentized

# region FacilityEventStateTypeGQLModel
@strawberry.federation.type(
    keys=["id"], description="""Entity representing a facility type"""
)
class FacilityEventStateTypeGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).EventFacilityStateType

# endregion