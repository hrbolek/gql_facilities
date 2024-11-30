
import strawberry

@strawberry.type(description="""Type for query root""")
class Query:

    from .FacilityGQLModel import (
        facility_by_id,
        facility_page
    )

    from .FacilityTypeGQLModel import (
        facility_type_by_id,
        facility_type_page
    )
