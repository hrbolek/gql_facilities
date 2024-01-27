from typing import List, Union, Optional, Annotated
import typing
import strawberry as strawberry
import datetime
import dataclasses
from uoishelpers.resolvers import createInputs

from ._GraphResolvers import (
    getLoadersFromInfo,
    
    IDType,

    resolve_reference,
    resolve_id,
    resolve_name,
    resolve_name_en,
    resolve_lastchange,
    resolve_created,
    resolve_createdby,
    resolve_changedby,

    asPage,
    
    encapsulateInsert,
    encapsulateUpdate    
    )

GroupGQLModel = Annotated["GroupGQLModel", strawberry.lazy(".GraphTypeDefinitionsExt")]
GroupGQLModel = Annotated["GroupGQLModel", strawberry.lazy(".GraphTypeDefinitionsExt")]

# region FacilityGQLModel
@strawberry.federation.type(
    keys=["id"], description="""Entity representing a Facility"""
)
class FacilityGQLModel:
    @classmethod
    def getLoader(info: strawberry.types.Info):
        return getLoadersFromInfo(info).facilities

    resolve_reference = resolve_reference
    id = resolve_id
    name = resolve_name
    name_en = resolve_name_en

    lastchange = resolve_lastchange
    created = resolve_created
    createdby = resolve_createdby
    changedby = resolve_changedby

    @strawberry.field(
        description="""Facility full name assigned by an administrator"""
        )
    def label(self) -> Optional[str]:
        return self.label

    # address
    @strawberry.field(
        description="""Facility address"""
    )
    def address(self) -> Optional[str]:
        return self.address

    # valid
    @strawberry.field(
        description="""is the facility still valid"""
    )
    def valid(self) -> Optional[bool]:
        return self.valid

    @strawberry.field(
        description="""Facility's capacity"""
    )
    def capacity(self) -> Optional[int]:
        return self.capacity

    # manager_id

    # address
    @strawberry.field(
        description="""Facility geometry (SVG)"""
    )
    def geometry(self) -> Optional[str]:
        return self.geometry

    @strawberry.field(
        description="""Facility geo address (WGS84+zoom)"""
    )
    def geolocation(self) -> Optional[str]:
        return self.geolocation

    @strawberry.field(description="""Facility type""")
    async def type(self, info: strawberry.types.Info) -> Optional["FacilityTypeGQLModel"]:
        result = await FacilityTypeGQLModel.resolve_reference(info=info, id=self.facilitytype_id)
        return result

    @strawberry.field(description="""Intermediate entity linking the event and facility""")
    async def event_state(self, info: strawberry.types.Info) -> Optional["FacilityEventStateTypeGQLModel"]:
        loader = FacilityEventStateTypeGQLModel.getLoader(info)
        result = await loader.load(self.id)
        return result

    @strawberry.field(description="""Facility above this""")
    async def master_facility(self, info: strawberry.types.Info) -> Optional["FacilityGQLModel"]:
        result = await FacilityGQLModel.resolve_reference(info=info, id=self.master_facility_id)
        return result

    @strawberry.field(description="""Facilities inside facility (like buildings in an areal)""")
    async def sub_facilities(
        self, info: strawberry.types.Info
    ) -> List["FacilityGQLModel"]:
        loader = FacilityGQLModel.getLoader(info)
        result = await loader.load(master_facility_id = self.id)
        return result

    @strawberry.field(description="""Facility management group""")
    async def group(self, info: strawberry.types.Info) -> Optional["GroupGQLModel"]:
        from .GraphTypeDefinitionsExt import GroupGQLModel
        return await GroupGQLModel.resolve_reference(id=self.group_id)
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
    resolve_reference = resolve_reference

    id = resolve_id
    name = resolve_name
    name_en = resolve_name_en

    lastchange = resolve_lastchange
    created = resolve_created
    createdby = resolve_createdby
    changedby = resolve_changedby

# endregion
    
# region FacilityEventGQLModel
@strawberry.federation.type(
    keys=["id"], description="""Entity representing the link between facility and event"""
)
class FacilityEventGQLModel:
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info).facilities_events
    resolve_reference = resolve_reference

    id = resolve_id
    name = resolve_name
    name_en = resolve_name_en

    lastchange = resolve_lastchange
    created = resolve_created
    createdby = resolve_createdby
    changedby = resolve_changedby

    @strawberry.field(description="""the event""")
    async def event(self) -> Optional["EventGQLModel"]:
        from .GraphTypeDefinitionsExt import EventGQLModel
        return await EventGQLModel.resolve_reference(id=self.event_id)

    @strawberry.field(description="""the facility""")
    async def facility(self, info: strawberry.types.Info) -> Optional["FacilityGQLModel"]:
        #print()
        result = await FacilityGQLModel.resolve_reference(info=info, id=self.facility_id)
        return result

    @strawberry.field(description="""the facility state (reserved for an event, lesson planned etc.)""")
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
    resolve_reference = resolve_reference

    id = resolve_id
    name = resolve_name
    name_en = resolve_name_en

    lastchange = resolve_lastchange
    created = resolve_created
    createdby = resolve_createdby
    changedby = resolve_changedby

# endregion
    

###########################################################################################################################
#
# zde definujte svuj Query model
#
###########################################################################################################################

# region Facility
@strawberry.field(description="""Finds an facility their id""")
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


@strawberry.field(description="""Finds an facility their id""")
@asPage
async def facility_page(
    self, info: strawberry.types.Info, 
    skip: Optional[int] = 0, limit: Optional[int] = 10, 
    where: Optional[FacilityInputFilter] = None
) -> List[FacilityGQLModel]:
    return FacilityGQLModel.getLoader(info)
    
# endregion

# region FacilityType
@strawberry.field(description="""Finds an workflow by their id""")
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

@strawberry.field(description="""Returns all facility types""")
@asPage
async def facility_type_page(
    self, info: strawberry.types.Info, 
    skip: Optional[int] = 0, limit: Optional[int] = 10, 
    where: Optional[FacilityTypeInputFilter] = None
) -> List[FacilityTypeGQLModel]:
    return FacilityTypeGQLModel.getLoader(info)

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


@strawberry.type(description="""Type for query root""")
class Query:
    @strawberry.field(description="""Finds an workflow by their id""")
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
@strawberry.input
class FacilityInsertGQLModel:
    name: str
    facilitytype_id: Optional[IDType] = None
    id: Optional[IDType] = None
    startdate: Optional[datetime.datetime] = datetime.datetime.now()
    enddate: Optional[datetime.datetime] = datetime.datetime.now() + datetime.timedelta(minutes = 30)
    name_en: Optional[str] = ""
    label: Optional[str] = ""
    address: Optional[str] = ""
    valid: Optional[bool] = True
    capacity: Optional[int] = 0
    geometry: Optional[str] = ""
    geolocation: Optional[str] = ""

    group_id: Optional[IDType] = None
    master_facility_id: Optional[IDType] = None

@strawberry.input
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
    
@strawberry.type
class FacilityResultGQLModel:
    id: IDType = None
    msg: str = None

    @strawberry.field(description="""Result of user operation""")
    async def facility(self, info: strawberry.types.Info) -> Union[FacilityGQLModel, None]:
        result = await FacilityGQLModel.resolve_reference(info, self.id)
        return result


@strawberry.mutation
async def facility_insert(self, info: strawberry.types.Info, facility: FacilityInsertGQLModel) -> FacilityResultGQLModel:
    return await encapsulateInsert(info, FacilityGQLModel.getLoader(info), facility, FacilityResultGQLModel(msg="ok", id=facility.id))

@strawberry.mutation
async def facility_update(self, info: strawberry.types.Info, facility: FacilityUpdateGQLModel) -> FacilityResultGQLModel:
    return await encapsulateUpdate(info, FacilityGQLModel.getLoader(info), facility, FacilityResultGQLModel(msg="ok", id=facility.id))
    
# endregion
    
@strawberry.federation.type(extend=True)
class Mutation:
    facility_insert = facility_insert
    facility_update = facility_update
    
###########################################################################################################################
#
# Schema je pouzito v main.py, vsimnete si parametru types, obsahuje vyjmenovane modely. Bez explicitniho vyjmenovani
# se ve schema objevi jen ty struktury, ktere si strawberry dokaze odvodit z Query. Protoze v teto konkretni implementaci
# nektere modely nejsou s Query propojene je potreba je explicitne vyjmenovat. Jinak ve federativnim schematu nebude
# dostupne rozsireni, ktere tento prvek federace implementuje.
#
###########################################################################################################################

schema = strawberry.federation.Schema(Query, mutation = Mutation)
