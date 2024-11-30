import pytest
import logging
import uuid
import sqlalchemy
import json
import datetime


myquery = """
{
  me {
    id
    fullname
    email
    roles {
      valid
      group { id name }
      roletype { id name }
    }
  }
}"""

@pytest.mark.asyncio
async def test_result_test(NoRole_UG_Server):
    # response = {}
    response = await NoRole_UG_Server(query=myquery, variables={})
    
    print("response", response, flush=True)
    logging.info(f"response {response}")
    pass

from .gt_utils import createByIdTest2, createUpdateTest2, createTest2, createDeleteTest2

test_facility_by_id = createByIdTest2(tableName="facilities")
test_facility_coverage = createByIdTest2(tableName="facilities", queryName="coverage")
test_facility_update = createUpdateTest2(tableName="facilities", variables={"name": "newname"})
test_facility_create = createTest2(tableName="facilities", queryName="create", variables={"name": "newname"})
test_facility_delete = createDeleteTest2(tableName="facilities", variables={"id": "18375c23-767c-4c1e-adb6-9b2beb463533", "name": "newname"})

test_facility_type_by_id = createByIdTest2(tableName="facilitytypes")
# test_facility_type_page = createTest2(tableName="facilitytypes", queryName="readp")
test_facility_type_create = createTest2(tableName="facilitytypes", queryName="create", variables={"name": "newname"})
test_facility_type_update = createUpdateTest2(tableName="facilitytypes", variables={"name": "newname"})
test_facility_type_delete = createDeleteTest2(tableName="facilitytypes", variables={"name": "newname"})
