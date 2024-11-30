import typing
import strawberry

sentinel = "893b4f74-c4b7-4b35-b638-6592b5ff48ea"
class VectorResolver:
    @classmethod
    def __class_getitem__(cls, item):
        listType = item
        # print(f"PageResolver[{listType}]", flush=True)
        def result(*, fkey_field_name, whereType):
            # print(f"PageResolver.result", flush=True)
            async def resolver(self, info: strawberry.Info, skip: typing.Optional[int]=0, limit: typing.Optional[int]=10, orderby: typing.Optional[str]=None, where: typing.Optional[whereType]=None) -> typing.List[listType]:
                value = getattr(self, fkey_field_name, sentinel)
                assert (value != sentinel), f"missing value {listType}.{fkey_field_name}"
                extendedfilter = {fkey_field_name: value}
                loader = listType.getLoader(info=info)
                where = None if where is None else strawberry.asdict(where)
                results = await loader.page(skip=skip, limit=limit, orderby=orderby, where=where, extendedfilter=extendedfilter)
                return (listType.from_dataclass(result) for result in results)        
            return resolver       
        return result

class PageResolver:
    @classmethod
    def __class_getitem__(cls, item):
        listType = item
        # print(f"PageResolver[{listType}]", flush=True)
        def result(*, whereType):
            # print(f"PageResolver.result", flush=True)
            async def resolver(self, info: strawberry.Info, skip: typing.Optional[int]=0, limit: typing.Optional[int]=10, orderby: typing.Optional[str]=None, where: typing.Optional[whereType]=None) -> typing.List[listType]:
                # listType = type(self)
                # listType = self.type_arg
                loader = listType.getLoader(info=info)
                where = None if where is None else strawberry.asdict(where)
                results = await loader.page(skip=skip, limit=limit, orderby=orderby, where=where)
                return (listType.from_dataclass(result) for result in results)        
            return resolver       
        return result