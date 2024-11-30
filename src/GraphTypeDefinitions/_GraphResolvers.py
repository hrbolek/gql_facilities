import strawberry
import uuid
import datetime
import typing
import logging

IDType = uuid.UUID

from uoishelpers.gqlpermissions import OnlyForAuthentized

def getLoadersFromInfo(info: strawberry.types.Info):
    result = info.context.get("loaders", None)
    assert result is not None, "Loaders are asked for but not present in context, check context preparation"
    return result

def getUserFromInfo(info: strawberry.types.Info):
    result = info.context.get("user", None)
    if result is None:
        request = info.context.get("request", None)
        assert request is not None, "request should be in context, something is wrong"
        result = request.scope.get("user", None)
    assert result is not None, "User is wanted but not present in context or in request.scope, check it"
    return result


@classmethod
async def resolve_reference(cls, info: strawberry.types.Info, id: IDType):
    if id is None: return None
    if isinstance(id, str): id = IDType(id)
    loader = cls.getLoader(info)
    dbrow = await loader.load(id)
    result = None
    if dbrow is not None:
        result = cls(_data=dbrow)
        # result._data = dbrow
        # result._type_definition = cls._type_definition  # little hack :)
        # result.__strawberry_definition__ = cls.__strawberry_definition__  # little hack :)
    return result

def resolve_field(*, self, field_name):
    _data = getattr(self, "_data", self)
    value = getattr(_data, field_name, None)
    # print(f"query for {field_name}@{_data}={value}")
    return value


from strawberry.types.base import StrawberryList, StrawberryOptional
def resolveResultType(info: strawberry.types.Info):
    return_type = info.return_type
    if (return_type.__class__.__name__ == "StrawberryOptional"):
        return_type = return_type.of_type

    if (return_type.__class__.__name__ == "StrawberryList"):
        return_type = return_type.of_type

    if (isinstance(return_type, strawberry.LazyType)):
        return_type = return_type.resolve_type()
    return return_type


def default_scalar_resolver(*, fkey_field_name):
    cache = {"executor": None}
    def getexecutor(info: strawberry.Info, cache=cache):
        executor = cache["executor"]
        if executor is None:
            return_type = resolveResultType(info)
            executor = return_type.resolve_reference
            cache["executor"] = executor
        return executor
    async def result(self, info: strawberry.types.Info):
        value = resolve_field(self=self, field_name=fkey_field_name)
        executor = getexecutor(info=info)
        gql_value = await executor(info=info, id=value)
        return gql_value
    return result

def default_vector_resolver(*, fkey_field_name, whereType):
    async def result(self, info: strawberry.Info, skip: typing.Optional[int]=0, limit: typing.Optional[int]=10, orderby: typing.Optional[str]=None, where: typing.Optional[whereType]=None):
        value = resolve_field(self=self, field_name="id")
        extendedfilter = {fkey_field_name: value}
        listType = type(self)
        loader = listType.getLoader(info=info)
        where = None if where is None else strawberry.asdict(where)
        results = await loader.page(skip=skip, limit=limit, orderby=orderby, where=where, extendedfilter=extendedfilter)
        return (listType(result) for result in results)
    return result

sentinel = "893b4f74-c4b7-4b35-b638-6592b5ff48ea"
class VectorResolver:
    @classmethod
    def __class_getitem__(cls, item):
        listType = item
        print(f"PageResolver[{listType}]", flush=True)
        def result(*, fkey_field_name, whereType):
            print(f"PageResolver.result", flush=True)
            async def resolver(self, info: strawberry.Info, skip: typing.Optional[int]=0, limit: typing.Optional[int]=10, orderby: typing.Optional[str]=None, where: typing.Optional[whereType]=None) -> typing.List[listType]:
                value = getattr(self, fkey_field_name, sentinel)
                assert (value != sentinel), f"missing value {listType}.{fkey_field_name}"
                extendedfilter = {fkey_field_name: value}
                loader = listType.getLoader(info=info)
                where = None if where is None else strawberry.asdict(where)
                results = await loader.page(skip=skip, limit=limit, orderby=orderby, where=where, extendedfilter=extendedfilter)
                return (listType.from_sqlalchemy(result) for result in results)        
            return resolver       
        return result

class PageResolver:
    @classmethod
    def __class_getitem__(cls, item):
        listType = item
        print(f"PageResolver[{listType}]", flush=True)
        def result(*, whereType):
            print(f"PageResolver.result", flush=True)
            async def resolver(self, info: strawberry.Info, skip: typing.Optional[int]=0, limit: typing.Optional[int]=10, orderby: typing.Optional[str]=None, where: typing.Optional[whereType]=None) -> typing.List[listType]:
                # listType = type(self)
                # listType = self.type_arg
                loader = listType.getLoader(info=info)
                where = None if where is None else strawberry.asdict(where)
                results = await loader.page(skip=skip, limit=limit, orderby=orderby, where=where)
                return (listType.from_sqlalchemy(result) for result in results)        
            return resolver       
        return result

@strawberry.field(
    description="""Entity primary key""",
    permission_classes=[OnlyForAuthentized]
    )
def resolve_id(self) -> IDType:
    return resolve_field(self=self, field_name="id")
    # return self.id


@strawberry.field(
    description="""Name """,
    permission_classes=[OnlyForAuthentized]
    )
def resolve_name(self) -> typing.Optional[str]:
    return resolve_field(self=self, field_name="name")
    # return self.name

@strawberry.field(
    description="""English name""",
    permission_classes=[OnlyForAuthentized]
    )
def resolve_name_en(self) -> typing.Optional[str]:
    return resolve_field(self=self, field_name="name_en")
    # result = self.name_en if self.name_en else ""
    # return result

@strawberry.field(
    description="""Time of last update""",
    permission_classes=[OnlyForAuthentized]
    )
def resolve_lastchange(self) -> typing.Optional[datetime.datetime]:
    return resolve_field(self=self, field_name="lastchange")
    # return self.lastchange

@strawberry.field(
    description="""Time of entity introduction""",
    permission_classes=[OnlyForAuthentized]
    )
def resolve_created(self) -> typing.Optional[datetime.datetime]:
    return resolve_field(self=self, field_name="created")
    # return self.created

UserGQLModel = typing.Annotated["UserGQLModel", strawberry.lazy(".GraphTypeDefinitionsExt")]

async def resolve_user(user_id):
    from .GraphTypeDefinitionsExt import UserGQLModel
    result = None if user_id is None else await UserGQLModel.resolve_reference(id=user_id, info=None)
    return result
    
@strawberry.field(description="""Who created entity""",
        permission_classes=[OnlyForAuthentized])
async def resolve_createdby(self) -> typing.Optional["UserGQLModel"]:
    createdby = resolve_field(self=self, field_name="createdby")
    return await resolve_user(createdby)

@strawberry.field(description="""Who made last change""",
        permission_classes=[OnlyForAuthentized])
async def resolve_changedby(self) -> typing.Optional["UserGQLModel"]:
    changedby = resolve_field(self=self, field_name="changedby")
    return await resolve_user(changedby)

RBACObjectGQLModel = typing.Annotated["RBACObjectGQLModel", strawberry.lazy(".GraphTypeDefinitionsExt")]
@strawberry.field(description="""Who made last change""",
        permission_classes=[OnlyForAuthentized]
        )
async def resolve_rbacobject(self, info: strawberry.types.Info) -> typing.Optional[RBACObjectGQLModel]:
    from .GraphTypeDefinitionsExt import RBACObjectGQLModel
    rbacobject = resolve_field(self=self, field_name="rbacobject")
    result = await RBACObjectGQLModel.resolve_reference(info, rbacobject)
    return result

resolve_result_id: IDType = strawberry.field(description="primary key of CU operation object")
resolve_result_msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")

from inspect import signature
import inspect 
from functools import wraps

def asPage(field, *, extendedfilter=None):
    def decorator(field):
        # print(field.__name__, field.__annotations__)
        signatureField = signature(field)
        return_annotation = signatureField.return_annotation

        skipParameter = signatureField.parameters.get("skip", None)
        skipParameterDefault = 0
        if skipParameter:
            skipParameterDefault = skipParameter.default

        limitParameter = signatureField.parameters.get("limit", None)
        limitParameterDefault = 10
        if limitParameter:
            limitParameterDefault = limitParameter.default

        whereParameter = signatureField.parameters.get("where", None)
        whereParameterDefault = None
        whereParameterAnnotation = str
        if whereParameter:
            whereParameterDefault = whereParameter.default
            whereParameterAnnotation = whereParameter.annotation

        async def foreignkeyVectorSimple(
            self, info: strawberry.types.Info,
            skip: typing.Optional[int] = skipParameterDefault,
            limit: typing.Optional[int] = limitParameterDefault
        ) -> signature(field).return_annotation:
            loader = await field(self, info)
            results = await loader.page(skip=skip, limit=limit, extendedfilter=extendedfilter)
            return results
        foreignkeyVectorSimple.__name__ = field.__name__
        foreignkeyVectorSimple.__doc__ = field.__doc__

        async def foreignkeyVectorComplex(
            self, info: strawberry.types.Info, 
            where: whereParameterAnnotation = None, 
            #where: typing.Optional[whereParameterAnnotation] = whereParameterDefault, 
            #where: typing.Optional[str] = None, 
            orderby: typing.Optional[str] = None, 
            desc: typing.Optional[bool] = None, 
            skip: typing.Optional[int] = skipParameterDefault,
            limit: typing.Optional[int] = limitParameterDefault
        ) -> signatureField.return_annotation:
            # logging.info(f"waiting for a loader {where}")
            wf = None if where is None else strawberry.asdict(where)
            loader = await field(self, info, where=wf)    
            # logging.info(f"got a loader {loader}")
            # wf = None if where is None else strawberry.asdict(where)
            results = await loader.page(skip=skip, limit=limit, where=wf, orderby=orderby, desc=desc, extendedfilter=extendedfilter)
            return results
        foreignkeyVectorComplex.__name__ = field.__name__
        foreignkeyVectorComplex.__doc__ = field.__doc__
        foreignkeyVectorComplex.__module__ = field.__module__
        
        if return_annotation._name == "List":
            return foreignkeyVectorComplex if whereParameter else foreignkeyVectorSimple
        else:
            raise Exception("Unable to recognize decorated function, I am sorry")

    return decorator(field) if field else decorator


async def encapsulateInsert(info, loader, entity, result):
    actinguser = getUserFromInfo(info)
    id = uuid.UUID(actinguser["id"])
    entity.createdby = id

    row = await loader.insert(entity)
    assert result.msg is not None, "result msg must be predefined (Operation Insert)"
    result.id = row.id
    return result

async def encapsulateUpdate(info, loader, entity, result):
    actinguser = getUserFromInfo(info)
    id = uuid.UUID(actinguser["id"])
    entity.changedby = id

    row = await loader.update(entity)
    result.id = entity.id if result.id is None else result.id 
    result.msg = "ok" if row is not None else "fail"
    return result

# def asInsert(field):
#     def decorator(field):
#         print(field.__name__, field.__annotations__)
#         signatureField = signature(field)
#         return_annotation = signatureField.return_annotation

#         print("signatureField.parameters", signatureField.parameters)

#         entityParameterName = list(signatureField.parameters.keys())[2]
#         print("signatureField.entityParameter", entityParameterName)
#         entityParameter = signatureField.parameters[entityParameterName]
#         print("signatureField.entityParameter", entityParameter)

#         async def Insert(
#             self, info: strawberry.types.Info,
#             entity
#         ) -> return_annotation:
#             print("I am working")
#             loader = field(self, info)
#             print("loader", loader)
#             return None
        

#         Insert.__name__ = field.__name__
#         Insert.__doc__ = field.__doc__
#         Insert.__module__ = field.__module__

        
#         return Insert

#     return decorator(field)

def asForeignList(*, foreignKeyName: str):
    assert foreignKeyName is not None, "foreignKeyName must be defined"
    def decorator(field):
        print(field.__name__, field.__annotations__)
        signatureField = signature(field)
        return_annotation = signatureField.return_annotation

        skipParameter = signatureField.parameters.get("skip", None)
        skipParameterDefault = skipParameter.default if skipParameter else 0

        limitParameter = signatureField.parameters.get("limit", None)
        limitParameterDefault = limitParameter.default if limitParameter else 10

        whereParameter = signatureField.parameters.get("where", None)
        whereParameterDefault = whereParameter.default if whereParameter else None
        whereParameterAnnotation = whereParameter.annotation if whereParameter else str

        async def foreignkeyVectorSimple(
            self, info: strawberry.types.Info,
            skip: typing.Optional[int] = skipParameterDefault,
            limit: typing.Optional[int] = limitParameterDefault
        ) -> signature(field).return_annotation:
            extendedfilter = {}
            extendedfilter[foreignKeyName] = self.id
            loader = field(self, info)
            if inspect.isawaitable(loader):
                loader = await loader
            results = await loader.page(skip=skip, limit=limit, extendedfilter=extendedfilter)
            return results
        foreignkeyVectorSimple.__name__ = field.__name__
        foreignkeyVectorSimple.__doc__ = field.__doc__
        foreignkeyVectorSimple.__module__ = field.__module__

        async def foreignkeyVectorComplex(
            self, info: strawberry.types.Info, 
            where: whereParameterAnnotation = whereParameterDefault, 
            orderby: typing.Optional[str] = None, 
            desc: typing.Optional[bool] = None, 
            skip: typing.Optional[int] = skipParameterDefault,
            limit: typing.Optional[int] = limitParameterDefault
        ) -> signatureField.return_annotation:
            extendedfilter = {}
            extendedfilter[foreignKeyName] = self.id
            loader = field(self, info)
            if inspect.isawaitable(loader):
                loader = await loader
            
            wf = None if where is None else strawberry.asdict(where)
            results = await loader.page(skip=skip, limit=limit, where=wf, orderby=orderby, desc=desc, extendedfilter=extendedfilter)
            return results
        foreignkeyVectorComplex.__name__ = field.__name__
        foreignkeyVectorComplex.__doc__ = field.__doc__
        foreignkeyVectorComplex.__module__ = field.__module__

        async def foreignkeyVectorComplex2(
            self, info: strawberry.types.Info, 
            where: whereParameterAnnotation = whereParameterDefault, 
            orderby: typing.Optional[str] = None, 
            desc: typing.Optional[bool] = None, 
            skip: typing.Optional[int] = skipParameterDefault,
            limit: typing.Optional[int] = limitParameterDefault
        ) -> signatureField.return_annotation: #typing.List[str]:
            extendedfilter = {}
            extendedfilter[foreignKeyName] = self.id
            loader = field(self, info)
            
            wf = None if where is None else strawberry.asdict(where)
            results = await loader.page(skip=skip, limit=limit, where=wf, orderby=orderby, desc=desc, extendedfilter=extendedfilter)
            return results
        foreignkeyVectorComplex2.__module__ = field.__module__
        if return_annotation._name == "List":
            return foreignkeyVectorComplex if whereParameter else foreignkeyVectorSimple
        else:
            raise Exception("Unable to recognize decorated function, I am sorry")

    return decorator
# def createAttributeScalarResolver(

# def createAttributeScalarResolver(
#     scalarType: None = None, 
#     foreignKeyName: str = None,
#     description="Retrieves item by its id",
#     permission_classes=()
#     ):

#     assert scalarType is not None
#     assert foreignKeyName is not None

#     @strawberry.field(description=description, permission_classes=permission_classes)
#     async def foreignkeyScalar(
#         self, info: strawberry.types.Info
#     ) -> typing.Optional[scalarType]:
#         # 👇 self must have an attribute, otherwise it is fail of definition
#         assert hasattr(self, foreignKeyName)
#         id = getattr(self, foreignKeyName, None)
        
#         result = None if id is None else await scalarType.resolve_reference(info=info, id=id)
#         return result
#     return foreignkeyScalar

# def createAttributeVectorResolver(
#     scalarType: None = None, 
#     whereFilterType: None = None,
#     foreignKeyName: str = None,
#     loaderLambda = lambda info: None, 
#     description="Retrieves items paged", 
#     skip: int=0, 
#     limit: int=10):

#     assert scalarType is not None
#     assert foreignKeyName is not None

#     @strawberry.field(description=description)
#     async def foreignkeyVector(
#         self, info: strawberry.types.Info,
#         skip: int = skip,
#         limit: int = limit,
#         where: typing.Optional[whereFilterType] = None
#     ) -> typing.List[scalarType]:
        
#         params = {foreignKeyName: self.id}
#         loader = loaderLambda(info)
#         assert loader is not None
        
#         wf = None if where is None else strawberry.asdict(where)
#         result = await loader.page(skip=skip, limit=limit, where=wf, extendedfilter=params)
#         return result
#     return foreignkeyVector

def createRootResolver_by_id(scalarType: None, description="Retrieves item by its id"):
    assert scalarType is not None
    @strawberry.field(description=description)
    async def by_id(
        self, info: strawberry.types.Info, id: IDType
    ) -> typing.Optional[scalarType]:
        result = await scalarType.resolve_reference(info=info, id=id)
        return result
    return by_id

def createRootResolver_by_page(
    scalarType: None, 
    whereFilterType: None,
    loaderLambda = lambda info: None, 
    description="Retrieves items paged", 
    skip: int=0, 
    limit: int=10,
    order_by: typing.Optional[str] = None,
    desc: typing.Optional[bool] = None):

    assert scalarType is not None
    assert whereFilterType is not None
    
    @strawberry.field(description=description)
    async def paged(
        self, info: strawberry.types.Info, 
        skip: int=skip, limit: int=limit, where: typing.Optional[whereFilterType] = None
    ) -> typing.List[scalarType]:
        loader = loaderLambda(info)
        assert loader is not None
        wf = None if where is None else strawberry.asdict(where)
        result = await loader.page(skip=skip, limit=limit, where=wf, orderby=order_by, desc=desc)
        return result
    return paged


#TODO dont know how to test it - hunting coverage
# from sqlalchemy.future import select
# from DBDefinitions import EventModel, EventGroupModel, PresenceModel

# def create_statement_for_group_events(id, startdate=None, enddate=None):
#     statement = select(EventModel).join(EventGroupModel)
#     if startdate is not None:
#         statement = statement.filter(EventModel.startdate >= startdate)
#     if enddate is not None:
#         statement = statement.filter(EventModel.enddate <= enddate)
#     statement = statement.filter(EventGroupModel.group_id == id)

#     return statement

# #odstranit?
# def create_statement_for_user_events(id, startdate=None, enddate=None):
#     statement = select(EventModel).join(PresenceModel)
#     if startdate is not None:
#         statement = statement.filter(EventModel.startdate >= startdate)
#     if enddate is not None:
#         statement = statement.filter(EventModel.enddate <= enddate)
#     statement = statement.filter(PresenceModel.user_id == id)
#     return statement

# from uoishelpers.dataloaders import prepareSelect
# def create_statement_for_user_events2(id, where: dict= None):
#     if where is None:
#         statement = select(EventModel)
#     else:    
#         statement = prepareSelect(EventModel, where)
#     statement = statement.join(PresenceModel)
#     statement = statement.filter(PresenceModel.user_id == id)
#     return statement

# async def resolvePresencesForEvent(session, id, invitationtypelist=[]):
#     statement = select(PresenceModel)
#     if len(invitationtypelist) > 0:
#         statement = statement.filter(PresenceModel.invitation_id.in_(invitationtypelist))
#     response = await session.execute(statement)
#     result = response.scalars()
#     return result