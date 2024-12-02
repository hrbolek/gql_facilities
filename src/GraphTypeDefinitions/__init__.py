import strawberry

import strawberry.extensions
from uoishelpers.gqlpermissions import RBACObjectGQLModel
###########################################################################################################################
#
# Schema je pouzito v main.py, vsimnete si parametru types, obsahuje vyjmenovane modely. Bez explicitniho vyjmenovani
# se ve schema objevi jen ty struktury, ktere si strawberry dokaze odvodit z Query. Protoze v teto konkretni implementaci
# nektere modely nejsou s Query propojene je potreba je explicitne vyjmenovat. Jinak ve federativnim schematu nebude
# dostupne rozsireni, ktere tento prvek federace implementuje.
#
###########################################################################################################################

from .UserGQLModel import UserGQLModel
from .GroupGQLModel import GroupGQLModel
from .EventGQLModel import EventGQLModel
from .BaseGQLModel import BaseGQLModel

from .query import Query
from .mutation import Mutation
schema = strawberry.federation.Schema(
    query=Query, 
    mutation=Mutation, 
    types=(UserGQLModel, GroupGQLModel, EventGQLModel, RBACObjectGQLModel, BaseGQLModel), 
    extensions=[]
)

from uoishelpers.schema import WhoAmIExtension, ProfilingExtension, PrometheusExtension
schema.extensions.append(WhoAmIExtension)
# schema.extensions.append(ProfilingExtension())        
# schema.extensions.append(PyInstrument())
# schema.extensions.append(PrometheusExtension(prefix="gql_facilities"))


from aiodataloader import DataLoader
import uuid


def getCacheKey(struct):
    return struct["id"]

class RBACLoader(DataLoader):
    def __init__(self, gqlclient):
        self.index = {}
        self.gqlclient = gqlclient
        super().__init__(
            get_cache_key=getCacheKey
        )

    async def batch_load_fn(self, structlist):
        index = {
            f'h{uuid.uuid4().hex}': item
            for item in structlist
        }
        lines = [
            f'{key}: rbacById(id: "{value["id"]}")'
            '{'
            f'judgement: userCanWithoutState(rolesNeeded: {value["roles"]})'
            '}'
            for key, value in index
        ]
        query = '{' + "\n".join(lines) + '}'
        gqlclient = self.gqlclient
        response = await gqlclient(query=query)
        assert "data" in response, f"get bad response while asking for RBAC {response}"
        responsedata = response["data"]
        result = [
            responsedata[key]["judgement"]
            for key in index.keys()
        ]
        return result

class RBACExtension(WhoAmIExtension):
    async def on_execute(self):
        self.execution_context.context["RBACLoader"] = RBACLoader(gqlclient=self.ug_query)

        # print("->on_execute", self.execution_context.query, flush=True)
        yield
        # print("on_execute->", whoami, flush=True)
