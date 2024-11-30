
import strawberry

@strawberry.type(description="""Type for query root""")
class Query:
    @strawberry.field(
            description="""Finds an workflow by their id""",
            )
    async def say_hello_facility(
        self, info: strawberry.types.Info, id: str
    ) -> None:
        result = f"Hello {id}"
        return result

    from .FacilityGQLModel import (
        facility_by_id,
        facility_page
    )

    from .FacilityTypeGQLModel import (
        facility_type_by_id,
        facility_type_page
    )
