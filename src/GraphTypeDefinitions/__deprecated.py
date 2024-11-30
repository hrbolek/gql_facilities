import asyncio
from typing import List, Union, Optional, Annotated
import typing
import strawberry as strawberry
import datetime
import dataclasses
import strawberry.types
from uoishelpers.resolvers import createInputs
from uoishelpers.gqlpermissions import OnlyForAuthentized
from sqlalchemy.orm import attributes

from ._GraphResolvers import (
    resolve_field,
    IDType,
    asPage,
    )

from uoishelpers.resolvers import (
    encapsulateDelete,
    encapsulateInsert,
    encapsulateUpdate,
    getLoadersFromInfo
)

from .BaseGQLModel import BaseGQLModel

GroupGQLModel = Annotated["GroupGQLModel", strawberry.lazy(".GraphTypeDefinitionsExt")]
EventGQLModel = Annotated["EventGQLModel", strawberry.lazy(".GraphTypeDefinitionsExt")]

# region FacilityGQLModel
@strawberry.federation.type(
    keys=["id"], description="""Entity representing a Facility"""
)
class FacilityGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).facilities

    _data: strawberry.Private[object]

    from ._GraphResolvers import (
        resolve_reference,
        resolve_id as id,

        resolve_name as name,
        resolve_name_en as name_en,

        resolve_lastchange as lastchange,
        resolve_created as created,

        resolve_createdby as createdby,
        resolve_changedby as changedby,
        resolve_rbacobject as rbacobject
    )

    label: Optional[str] = strawberry.field(
        description="""Facility full name assigned by an administrator""",
        permission_classes=[OnlyForAuthentized]
        )

    address: Optional[str] = strawberry.field(
        description="""Facility address""",
        permission_classes=[OnlyForAuthentized]
        )

    # valid
    valid: Optional[str] = strawberry.field(
        description="""is the facility still valid""",
        permission_classes=[OnlyForAuthentized]
    )

    capacity: Optional[int] = strawberry.field(
        description="""Facility's capacity""",
        permission_classes=[OnlyForAuthentized]
    )

    # manager_id

    # address
    geometry: Optional[str] = strawberry.field(
        description="""Facility geometry (SVG)""",
        permission_classes=[OnlyForAuthentized]
    )

    geolocation: Optional[str] = strawberry.field(
        description="""Facility geo address (WGS84+zoom)""",
        permission_classes=[OnlyForAuthentized]
    )

    @strawberry.field(
        description="""Facility type""",
        permission_classes=[OnlyForAuthentized]
        )
    async def type(self, info: strawberry.types.Info) -> Optional["FacilityTypeGQLModel"]:
        facilitytype_id = resolve_field(self=self, field_name="facilitytype_id")
        result = await FacilityTypeGQLModel.resolve_reference(info=info, id=facilitytype_id)
        return result

    @strawberry.field(
            description="""Intermediate entity linking the event and facility""",
            permission_classes=[OnlyForAuthentized]
            )
    async def event_state(self, info: strawberry.types.Info) -> List["FacilityEventStateTypeGQLModel"]:
        loader = FacilityEventStateTypeGQLModel.getLoader(info)
        loader = getLoadersFromInfo(info=info).facilities_events
        rows = await loader.filter_by(facility_id=self.id)
        futures = (FacilityEventStateTypeGQLModel.resolve_reference(info=info, id=row.state_id) for row in rows)
        results = await asyncio.gather(*futures)
        return results

    @strawberry.field(
            description="""Facility above this""",
            permission_classes=[OnlyForAuthentized]
            )
    async def master_facility(self, info: strawberry.types.Info) -> Optional["FacilityGQLModel"]:
        result = await FacilityGQLModel.resolve_reference(info=info, id=self.master_facility_id)
        return result

    @strawberry.field(
            description="""Facilities inside facility (like buildings in an areal)""",
            permission_classes=[OnlyForAuthentized])
    async def sub_facilities(
        self, info: strawberry.types.Info
    ) -> List["FacilityGQLModel"]:
        loader = FacilityGQLModel.getLoader(info)
        rows = await loader.filter_by(master_facility_id = self.id)
        futures = (FacilityGQLModel.resolve_reference(info=info, id=row.id) for row in rows)
        result = await asyncio.gather(*futures)
        return result

    @strawberry.field(
            description="""Facility management group""",
            permission_classes=[OnlyForAuthentized]
            )
    async def group(self, info: strawberry.types.Info) -> Optional["GroupGQLModel"]:
        from .GraphTypeDefinitionsExt import GroupGQLModel
        group_id = resolve_field(self=self, field_name="group_id")
        return await GroupGQLModel.resolve_reference(info, id=group_id)
# endregion
    
# region FacilityTypeGQLModel
from src.GraphResolvers import facilityTypePageStatement

@strawberry.federation.type(
    keys=["id"], description="""Entity representing a facility type"""
)
class FacilityTypeGQLModel:
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).facilitytypes

    _data: strawberry.Private[object]

    from ._GraphResolvers import (
        resolve_reference,
        resolve_id as id,

        resolve_name as name,
        resolve_name_en as name_en,

        resolve_lastchange as lastchange,
        resolve_created as created,

        resolve_createdby as createdby,
        resolve_changedby as changedby,
        resolve_rbacobject as rbacobject
    )

# endregion
    
# region FacilityEventGQLModel
@strawberry.federation.type(
    keys=["id"], description="""Entity representing the link between facility and event"""
)
class FacilityEventGQLModel:
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).facilities_events

    _data: strawberry.Private[object]

    from ._GraphResolvers import (
        resolve_reference,
        resolve_id as id,

        resolve_name as name,
        resolve_name_en as name_en,

        resolve_lastchange as lastchange,
        resolve_created as created,

        resolve_createdby as createdby,
        resolve_changedby as changedby,
        resolve_rbacobject as rbacobject
    )

    @strawberry.field(
            description="""the event""",
            permission_classes=[OnlyForAuthentized]
            )
    async def event(self) -> Optional["EventGQLModel"]:
        from .GraphTypeDefinitionsExt import EventGQLModel
        return await EventGQLModel.resolve_reference(id=self.event_id)

    @strawberry.field(
            description="""the facility""",
            permission_classes=[OnlyForAuthentized]
            )
    async def facility(self, info: strawberry.types.Info) -> Optional["FacilityGQLModel"]:
        #print()
        result = await FacilityGQLModel.resolve_reference(info=info, id=self.facility_id)
        return result

    @strawberry.field(
            description="""the facility state (reserved for an event, lesson planned etc.)""",
            permission_classes=[OnlyForAuthentized]
            )
    async def state(self, info: strawberry.types.Info) -> Optional["FacilityEventStateTypeGQLModel"]:
        result = await FacilityEventStateTypeGQLModel.resolve_reference(info=info, id=self.state_id)
        return result

# endregion
    
# region FacilityEventStateTypeGQLModel
@strawberry.federation.type(
    keys=["id"], description="""Entity representing a facility type"""
)
class FacilityEventStateTypeGQLModel:
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).facilityeventstatetypes

    _data: strawberry.Private[object]

    from ._GraphResolvers import (
        resolve_reference,
        resolve_id as id,

        resolve_name as name,
        resolve_name_en as name_en,

        resolve_lastchange as lastchange,
        resolve_created as created,

        resolve_createdby as createdby,
        resolve_changedby as changedby,
        resolve_rbacobject as rbacobject
    )

# endregion
    

###########################################################################################################################
#
# zde definujte svuj Query model
#
###########################################################################################################################

# region Facility
@strawberry.field(
        description="""Finds an facility their id""",
        permission_classes=[OnlyForAuthentized]
        )
async def facility_by_id(
    self, info: strawberry.types.Info, id: IDType
) -> Union[FacilityGQLModel, None]:
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

from ._GraphResolvers import default_page_resolver
# @strawberry.field(
#         description="""Finds paged facilities""",
#         permission_classes=[OnlyForAuthentized]
#         )
# @asPage
# async def facility_page(
#     self, info: strawberry.types.Info, 
#     skip: Optional[int] = 0, limit: Optional[int] = 10, 
#     where: Optional[FacilityInputFilter] = None
# ) -> List[FacilityGQLModel]:
#     return FacilityGQLModel.getLoader(info)
    
facility_page = strawberry.field(
        description="""Finds paged facilities""",
        permission_classes=[OnlyForAuthentized],
        graphql_type=List[FacilityGQLModel],
        resolver=default_page_resolver(whereType=FacilityInputFilter)
        )

# endregion

# region FacilityType
@strawberry.field(
        description="""Finds an facility type by its id""",
        permission_classes=[OnlyForAuthentized]
        )
async def facility_type_by_id(
    self, info: strawberry.types.Info, id: IDType
) -> Optional[FacilityTypeGQLModel]:
    result = await FacilityTypeGQLModel.resolve_reference(info=info, id=id)
    return result

@createInputs
@dataclasses.dataclass
class FacilityTypeInputFilter:
    name: str
    name_en: str

# @strawberry.field(
#         description="""Returns all facility types""",
#         permission_classes=[OnlyForAuthentized]
#         )
# @asPage
# async def facility_type_page(
#     self, info: strawberry.types.Info, 
#     skip: Optional[int] = 0, limit: Optional[int] = 10, 
#     where: Optional[FacilityTypeInputFilter] = None
# ) -> List[FacilityTypeGQLModel]:
#     return FacilityTypeGQLModel.getLoader(info)

facility_type_page = strawberry.field(
        description="""Returns all facility types""",
        permission_classes=[OnlyForAuthentized],
        graphql_type=List[FacilityTypeGQLModel],
        resolver=default_page_resolver(whereType=FacilityTypeInputFilter)
        )
# endregion

# region FacilityEventStateTypeGQLModel

# @strawberry.field(description="""Returns all facility event states""")
# async def facility_event_state_type_page(
#     self, info: strawberry.types.Info
# ) -> List[FacilityEventStateTypeGQLModel]:
#     loader = FacilityEventStateTypeGQLModel.getLoader(info)
#     result = await loader.execute_select(facilityStateTypePageStatement)
#     return result
# endregion



# region FacilityType
@strawberry.input(description="First datastructure for Facility type creation")
class FacilityTypeInsertGQLModel:
    name: str = strawberry.field(description="name of Facility type")
    name_en: Optional[str] = strawberry.field(description="english name of Facility type", default=None)
    id: Optional[IDType] = None
    createdby: strawberry.Private[IDType] = None
    rbacobject: Optional[IDType] = \
        strawberry.field(description="group_id or user_id defines access rights", default=None)


@strawberry.input(description="Datastructure for Facility type update")
class FacilityTypeUpdateGQLModel:
    id: IDType
    lastchange: datetime.datetime
    name: Optional[str] = None
    name_en: Optional[str] = None
    changedby: strawberry.Private[IDType] = None
    rbacobject: strawberry.Private[IDType] = None

@strawberry.type(description="""Result of facility type operation""")
class FacilityTypeResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(
            description="""Facility type""",
            permission_classes=[OnlyForAuthentized]
            )
    async def facility_type(self, info: strawberry.types.Info) -> Optional[FacilityTypeGQLModel]:
        result = await FacilityTypeGQLModel.resolve_reference(info, self.id)
        return result
    
from uoishelpers.gqlpermissions import (
    OnlyForAuthentized,
    MustBeOneOfPermission
    # OnlyForAdmins
)    
OnlyForAdmins = MustBeOneOfPermission("administrátor")
@strawberry.mutation(
    description="Creates new facility type",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def facility_type_insert(self, info: strawberry.types.Info, facility_type: FacilityTypeInsertGQLModel) -> FacilityTypeResultGQLModel:
    return await encapsulateInsert(info, FacilityTypeGQLModel.getLoader(info), facility_type, FacilityTypeResultGQLModel(id=None, msg="ok"))

@strawberry.mutation(
    description="Updates the facility type",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def facility_type_update(self, info: strawberry.types.Info, facility_type: FacilityTypeUpdateGQLModel) -> FacilityTypeResultGQLModel:
    return await encapsulateUpdate(info, FacilityTypeGQLModel.getLoader(info), facility_type, FacilityTypeResultGQLModel(id=None, msg="ok"))

@strawberry.mutation(
    description="Deletes the facility type",
    permission_classes=[
        OnlyForAuthentized,
        OnlyForAdmins
    ])
async def facility_type_delete(self, info: strawberry.types.Info, id: IDType) -> FacilityTypeResultGQLModel:
    return await encapsulateDelete(info, FacilityTypeGQLModel.getLoader(info), id, FacilityTypeResultGQLModel(id=None, msg="ok"))

# endregion



@strawberry.type(description="""Type for query root""")
class Query:
    @strawberry.field(
            description="""Finds an workflow by their id""",
            permission_classes=[OnlyForAuthentized]
            )
    async def say_hello_facility(
        self, info: strawberry.types.Info, id: IDType
    ) -> Union[str, None]:
        result = f"Hello {id}"
        return result

    facility_by_id = facility_by_id
    facility_page = facility_page

    facility_type_by_id = facility_type_by_id
    facility_type_page = facility_type_page

    # facility_event_state_type_page = facility_event_state_type_page




###########################################################################################################################
#
#
# Mutations
#
#
###########################################################################################################################

from typing import Optional
# region Facility
@strawberry.input(description="initial attributes for facility insert")
class FacilityInsertGQLModel:
    name: str = strawberry.field(description="name of the new facility")
    facilitytype_id: Optional[IDType] = strawberry.field(description="facility type", default=None)
    id: Optional[IDType] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    startdate: Optional[datetime.datetime] = datetime.datetime.now()
    enddate: Optional[datetime.datetime] = datetime.datetime.now() + datetime.timedelta(minutes = 30)
    name_en: Optional[str] = strawberry.field(description="english name of facility", default="")
    label: Optional[str] = strawberry.field(description="full name (including masterfacility)", default="")
    address: Optional[str] = strawberry.field(description="postal address", default="")
    valid: Optional[bool] = strawberry.field(description="if facility exists", default=True)
    capacity: Optional[int] = strawberry.field(description="facility capacity", default=0)
    geometry: Optional[str] = strawberry.field(description="SVG overlay for leaflet", default="")
    geolocation: Optional[str] = strawberry.field(description="WSGBLX;WGSBLY;ZOOM", default="")

    group_id: Optional[IDType] = strawberry.field(description="group which is responsible for management of this facility", default=None)
    master_facility_id: Optional[IDType] = strawberry.field(description="to which facility this facility belongs", default=None)

@strawberry.input(description="")
class FacilityUpdateGQLModel:
    lastchange: datetime.datetime
    id: IDType
    

    name: Optional[str] = None
    facilitytype_id: Optional[IDType] = None
    id: Optional[IDType] = None
    name_en: Optional[str] = None
    label: Optional[str] = None
    address: Optional[str] = None
    valid: Optional[bool] = None
    capacity: Optional[int] = None
    geometry: Optional[str] = None
    geolocation: Optional[str] = None

    group_id: Optional[IDType] = None
    master_facility_id: Optional[IDType] = None

    startdate: Optional[datetime.datetime] = None
    enddate: Optional[datetime.datetime] = None
    
@strawberry.type(description="")
class FacilityResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(
            description="""Result of user operation""",
            permission_classes=[OnlyForAuthentized]
            )
    async def facility(self, info: strawberry.types.Info) -> Union[FacilityGQLModel, None]:
        result = await FacilityGQLModel.resolve_reference(info, self.id)
        return result


@strawberry.mutation(
        description="",
        permission_classes=[
            OnlyForAuthentized,
            OnlyForAdmins
        ]
        )
async def facility_insert(self, info: strawberry.types.Info, facility: FacilityInsertGQLModel) -> FacilityResultGQLModel:
    return await encapsulateInsert(info, FacilityGQLModel.getLoader(info), facility, FacilityResultGQLModel(msg="ok", id=facility.id))

@strawberry.mutation(
        description="",
        permission_classes=[OnlyForAuthentized]
        )
async def facility_update(self, info: strawberry.types.Info, facility: typing.Annotated[FacilityUpdateGQLModel, strawberry.argument(description="desc")]) -> FacilityResultGQLModel:
    return await encapsulateUpdate(info, FacilityGQLModel.getLoader(info), facility, FacilityResultGQLModel(msg="ok", id=facility.id))
    
# endregion
    
@strawberry.federation.type(extend=True)
class Mutation:
    facility_insert = facility_insert
    facility_update = facility_update
    facility_type_insert = facility_type_insert
    facility_type_update = facility_type_update
    facility_type_delete = facility_type_delete
    
###########################################################################################################################
#
# Schema je pouzito v main.py, vsimnete si parametru types, obsahuje vyjmenovane modely. Bez explicitniho vyjmenovani
# se ve schema objevi jen ty struktury, ktere si strawberry dokaze odvodit z Query. Protoze v teto konkretni implementaci
# nektere modely nejsou s Query propojene je potreba je explicitne vyjmenovat. Jinak ve federativnim schematu nebude
# dostupne rozsireni, ktere tento prvek federace implementuje.
#
###########################################################################################################################

from .GraphTypeDefinitionsExt import UserGQLModel, GroupGQLModel, EventGQLModel, RBACObjectGQLModel
from .query import Query
from .mutation import Mutation
schema = strawberry.federation.Schema(
    query=Query, 
    mutation = Mutation, 
    types=(UserGQLModel, GroupGQLModel, EventGQLModel, RBACObjectGQLModel), 
    extensions=[]
)

from uoishelpers.schema import WhoAmIExtension
schema.extensions.append(WhoAmIExtension)
