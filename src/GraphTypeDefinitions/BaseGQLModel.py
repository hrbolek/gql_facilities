import uuid
import datetime
import typing
import strawberry
import dataclasses

from uoishelpers.resolvers import createInputs
from uoishelpers.gqlpermissions import OnlyForAuthentized, RBACObjectGQLModel

IDType = uuid.UUID
UserGQLModel = typing.Annotated["UserGQLModel", strawberry.lazy(".UserGQLModel")]


@classmethod
async def resolve_reference(cls, info: strawberry.types.Info, id: IDType, **otherData):
    _id = IDType(id) if isinstance(id, str) else id
    return None if id is None else cls(id=_id, **otherData)


@strawberry.federation.interface(
    keys=["id"], description="""Entity representing a Facility"""
)
class BaseGQLModel:
    @classmethod
    def get_table_resolvers(cls):
        # raise NotImplementedError()
        return {
            "id": lambda row: row.id,
            "lastchange": lambda row: row.lastchange,
            "created": lambda row: row.lastchange,
            "createdby_id": lambda row: row.createdby_id,
            "changedby_id": lambda row: row.changedby_id,
            "rbacobject_id": lambda row: row.rbacobject_id,
        }
    
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
        if id is None:
            return None

        _id = IDType(id) if isinstance(id, str) else id
        loader = cls.getLoader(info=info)
        db_row = await loader.load(_id)
        
        return None if db_row is None else cls.from_dataclass(db_row=db_row)
    
    @classmethod
    def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID, **otherdata):
        return cls.load_with_loader(info=info, id=id)
       
    id: typing.Optional[IDType] = strawberry.field(description="primary key", default=None)
    lastchange: typing.Optional[datetime.date] = strawberry.field(description="timestamp", default=None)
    created: typing.Optional[datetime.date] = strawberry.field(description="date & time of unit born", default=None)
    createdby_id: typing.Optional[IDType] = strawberry.field(description="who created this entity", default=None)
    changedby_id: typing.Optional[IDType] = strawberry.field(description="who changed this entity", default=None)
    rbacobject_id: typing.Optional[IDType] = strawberry.field(description="rbac ruling object", default=None)

    # _data: strawberry.Private[object]

    @strawberry.field(description="who created this entity")
    async def createdby(self) -> typing.Optional["UserGQLModel"]:
        from .UserGQLModel import UserGQLModel
        return None if self.changedby_id is None else UserGQLModel(id=self.createdby_id)

    @strawberry.field(description="who created this entity")
    async def changedby(self) -> typing.Optional["UserGQLModel"]:
        from .UserGQLModel import UserGQLModel
        return None if self.changedby_id is None else UserGQLModel(id=self.changedby_id)

    @strawberry.field(description="rbac holds relations of user")
    async def rbacobject(self) -> typing.Optional["RBACObjectGQLModel"]:
        return None if self.rbacobject_id is None else RBACObjectGQLModel(id=self.rbacobject_id)
