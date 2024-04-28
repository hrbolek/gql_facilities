import logging
from sqlalchemy.future import select
import strawberry
from typing import List, Any
from uuid import UUID
from functools import cached_property

import os

isDEMO = os.environ.get("DEMO", "True")

# def AsyncSessionFromInfo(info):
#     return info.context["session"]


# def UserFromInfo(info):
    # return info.context["user"]

"""
query ($id: ID!) {
  rolesOnUser(userId: $id) {
    ...role
  }
  rolesOnGroup(groupId: $id) {
    ...role
  }
}

fragment role on RoleGQLModel {
  valid
  roletype { id}
  user { id }
  group { id }
}
"""


class BasePermission(strawberry.permission.BasePermission):
    message = "User is not authenticated"

    async def has_permission(
        self, source, info: strawberry.types.Info, **kwargs
    ) -> bool:
        raise NotImplemented()
        # print("BasePermission", source)
        # print("BasePermission", self)
        # print("BasePermission", kwargs)
        # return True





from functools import cache
import aiohttp


rolelist = [
        {
            "name": "já",
            "name_en": "myself",
            "id": "05a3e0f5-f71e-4caa-8012-229d868aa8ca",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "administrátor",
            "name_en": "administrator",
            "id": "ced46aa4-3217-4fc1-b79d-f6be7d21c6b6",
            "category_id": "774690a0-56b3-45d9-9887-0989ed3de4c0"
        },
        {
            "name": "zpracovatel gdpr",
            "name_en": "gdpr user",
            "id": "b87aed46-dfc3-40f8-ad49-03f4138c7478",
            "category_id": "774690a0-56b3-45d9-9887-0989ed3de4c0"
        },
        {
            "name": "rektor",
            "name_en": "rector",
            "id": "ae3f0d74-6159-11ed-b753-0242ac120003",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "prorektor",
            "name_en": "vicerector",
            "id": "ae3f2886-6159-11ed-b753-0242ac120003",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "děkan",
            "name_en": "dean",
            "id": "ae3f2912-6159-11ed-b753-0242ac120003",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "proděkan",
            "name_en": "vicedean",
            "id": "ae3f2980-6159-11ed-b753-0242ac120003",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "vedoucí katedry",
            "name_en": "head of department",
            "id": "ae3f29ee-6159-11ed-b753-0242ac120003",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "vedoucí učitel",
            "name_en": "leading teacher",
            "id": "ae3f2a5c-6159-11ed-b753-0242ac120003",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "garant",
            "name_en": "grant",
            "id": "5f0c247e-931f-11ed-9b95-0242ac110002",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "garant (zástupce)",
            "name_en": "grant (deputy)",
            "id": "5f0c2532-931f-11ed-9b95-0242ac110002",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "garant předmětu",
            "name_en": "subject's grant",
            "id": "5f0c255a-931f-11ed-9b95-0242ac110002",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "přednášející",
            "name_en": "lecturer",
            "id": "5f0c2578-931f-11ed-9b95-0242ac110002",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        },
        {
            "name": "cvičící",
            "name_en": "trainer",
            "id": "5f0c2596-931f-11ed-9b95-0242ac110002",
            "category_id": "fd73596b-1043-46f0-837a-baa0734d64df"
        }
    ]

# async def getRoles(userId="", roleUrlEndpoint="http://localhost:8088/gql/", isDEMO=True):
#     query = """query($userid: UUID!){
#             roles: roleByUser(userId: $userid) {
#                 id
#                 valid
#                 roletype { id }
#                 group { id }
#                 user { id }
#             }
#         }
# """
#     variables = {"userid": userId}
#     headers = {}
#     json = {
#         "query": query,
#         "variables": variables
#     }

#     print("roleUrlEndpoint", roleUrlEndpoint)
#     async with aiohttp.ClientSession() as session:
#         print(f"query {roleUrlEndpoint} for json={json}")
#         async with session.post(url=roleUrlEndpoint, json=json, headers=headers) as resp:
#             print(resp.status)
#             if resp.status != 200:
#                 text = await resp.text()
#                 print(text)
#                 return []
#             else:
#                 respJson = await resp.json()

#     print(respJson)
    
#     assert respJson.get("errors", None) is None
#     respdata = respJson.get("data", None)
#     assert respdata is not None
#     roles = respdata.get("roles", None)
#     assert roles is not None
#     print("roles", roles)
#     return [*roles]

#     pass

import requests
# from utils.gql_ug_proxy import createProxy

def ReadAllRoles():
    GQLUG_ENDPOINT_URL = os.environ.get("GQLUG_ENDPOINT_URL", None)

    query = """query {result: roleTypePage(limit: 1000) {id, name, nameEn}}"""
    variables = {}

    json = {"query": query, "variables": variables}
    response = requests.post(url=GQLUG_ENDPOINT_URL, json=json)
    respJson = response.json()

    assert respJson.get("errors", None) is None, f'GQL response has errors: {respJson["errors"]}'
    respdata = respJson.get("data", None)
    assert respdata is not None, "during roles reading roles have not been readed"
    roles = respdata.get("result", None)
    assert roles is not None, "during roles reading roles have not been readed"
    print("roles", roles)
    roles = list(map(lambda item: {**item, "name_en": item["nameEn"]}, roles))
    return [*roles]

if not isDEMO:
    rolelist = ReadAllRoles()

roleIndex = { role["name_en"]: role["id"] for role in rolelist }

# async def ReadRoles(
#     userId="2d9dc5ca-a4a2-11ed-b9df-0242ac120003", 
#     roleUrlEndpoint="http://localhost:8088/gql/",
#     demo=True):
    
#     query = """query($userid: UUID!){
#             roles: roleByUser(userId: $userid) {
#                 id
#                 valid
#                 roletype { id }
#                 group { id }
#                 user { id }
#             }
#         }
# """
#     variables = {"userid": userId}
#     headers = {}
#     json = {
#         "query": query,
#         "variables": variables
#     }

#     print("roleUrlEndpoint", roleUrlEndpoint)
#     async with aiohttp.ClientSession() as session:
#         print(f"query {roleUrlEndpoint} for json={json}")
#         async with session.post(url=roleUrlEndpoint, json=json, headers=headers) as resp:
#             print(resp.status)
#             if resp.status != 200:
#                 text = await resp.text()
#                 print(text)
#                 return []
#             else:
#                 respJson = await resp.json()

#     print(respJson)
    
#     assert respJson.get("errors", None) is None
#     respdata = respJson.get("data", None)
#     assert respdata is not None
#     roles = respdata.get("roles", None)
#     assert roles is not None
#     print("roles", roles)
#     return [*roles]

# def WhereAuthorized(userRoles, roleIdsNeeded=[]):
    
#     # 👇 filtrace roli, ktere maji pozadovanou uroven autorizace
#     roletypesFiltered = filter(lambda item: item["roletype"]["id"] in roleIdsNeeded, userRoles)
#     # 👇 odvozeni, pro ktere skupiny ma tazatel patricnou uroven autorizace
#     groupsAuthorizedIds = map(lambda item: item["group"]["id"], roletypesFiltered)
#     # 👇 konverze na list
#     groupsAuthorizedIds = list(groupsAuthorizedIds)
#     # cokoliv se tyka techto skupin, na to autor muze
#     print("groupsAuthorizedIds", groupsAuthorizedIds)
#     return groupsAuthorizedIds

@cache
def RolesToList(roles: str = ""):
    roleNames = roles.split(";")
    roleNames = list(map(lambda item: item.strip(), roleNames))
    roleIdsNeeded = list(map(lambda roleName: roleIndex[roleName], roleNames))
    return roleIdsNeeded


@cache
def OnlyForAuthentized(isList=False):
    class OnlyForAuthentized(strawberry.permission.BasePermission):
        message = "User is not authenticated"

        async def has_permission(
            self, source, info: strawberry.types.Info, **kwargs
        ) -> bool:
            if self.isDEMO:
                print("DEMO Enabled, not for production")
                return True
            
            user = getUserFromInfo(info)
            return (False if user is None else True)
            #     return False        
            # return True
        
        def on_unauthorized(self):
            return ([] if isList else None)
            #     return []
            # else:
            #     return None
            
        @cached_property
        def isDEMO(self):
            DEMO = os.getenv("DEMO", None)
            return True if DEMO == "True" else False
            
    return OnlyForAuthentized

@cache
def RoleBasedPermission(roles: str = "", whatreturn=[]):
    roleIdsNeeded = RolesToList(roles)

    from .externals import RBACObjectGQLModel
    class RolebasedPermission(BasePermission):
        message = "User has not appropriate roles"

        def on_unauthorized(self) -> None:
            return whatreturn
        
        async def has_permission(
                self, source: Any, info: strawberry.types.Info, **kwargs: Any
            # self, source, info: strawberry.types.Info, **kwargs
            # self, source, **kwargs
        ) -> bool:
            # return False
            logging.info(f"has_permission {kwargs}")
            # assert False

            # GQLUG_ENDPOINT_URL = os.environ.get("GQLUG_ENDPOINT_URL", None)
            # assert GQLUG_ENDPOINT_URL is not None
            # proxy = createProxy(GQLUG_ENDPOINT_URL)

            print("RolebasedPermission", self) ##
            print("RolebasedPermission", source) ## self as in GQLModel
            print("RolebasedPermission", kwargs)

            assert hasattr(source, "rbacobject"), f"missing rbacobject on {source}"
            
            rbacobject = source.rbacobject
            
            #rbacobject
            assert rbacobject is not None, f"RoleBasedPermission cannot be used on {source} as it has None value"
            # rbacobject = "2d9dc5ca-a4a2-11ed-b9df-0242ac120003"


            ## zjistime, jake role jsou vztazeny k rbacobject 
            # print(response)

            authorizedroles = await RBACObjectGQLModel.resolve_roles(info=info, id=rbacobject)
            # authloader = getLoadersFromInfoFromInfo(info=info).authorizations
            # authloader.setTokenByInfo(info)
            # authorizedroles = await authloader.load(rbacobject)
            

            print("RolebasedPermission.rbacobject", rbacobject)
            # _ = await self.canEditGroup(session,  source.id, ...)
            print("RolebasedPermission.authorized", authorizedroles)
            
            # logging.info(f"RolebasedPermission.authorized {authorizedroles}")

            # user_id = "2d9dc5ca-a4a2-11ed-b9df-0242ac120003"
            user = getUserFromInfo(info)
            # logging.info(f"RolebasedPermission.authorized user {user}")
            user_id = user["id"]
            s = [r for r in authorizedroles if (r["roletype"]["id"] in roleIdsNeeded)and(r["user"]["id"] == user_id)]
            # s = [r for r in authorizedroles if r["roletype"]["id"] in roleIdsNeeded]
            
            logging.info(f"RolebasedPermission.authorized user {user} has roles {s}")

            if len(s) > 0:
                print("RolebasedPermission.access allowed")
            else:
                print("RolebasedPermission.access denied")
            print(s)
            print(roleIdsNeeded)
            isAllowed = len(s) > 0
            return isAllowed
        
    return RolebasedPermission


# class UserGDPRPermission(BasePermission):
#     message = "User is not authenticated"

#     async def has_permission(
#         self, source, info: strawberry.types.Info, **kwargs
#     ) -> bool:
#         print("UserGDPRPermission", source)
#         print("UserGDPRPermission", self)
#         print("UserGDPRPermission", kwargs)
#         return True
