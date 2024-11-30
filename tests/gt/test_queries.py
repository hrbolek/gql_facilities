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

from .gt_utils import (
    getQuery,

    createByIdTest2, 
    createUpdateTest2, 
    createTest2, 
    createDeleteTest2
)

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

test_reservation = createByIdTest2(tableName="facilities_events", variables={"id": "7dcf3d10-3a41-4c36-9700-99d885a1e474"})
test_reservation_create = createTest2(
    tableName="facilities_events", 
    queryName="create",
    variables={
        "id": "bab05e55-3f92-40b5-9272-4b66a368138f", 
        "facility_id": "7dcf3d10-3a41-4c36-9700-99d885a1e474",
        "event_id": "a64871f8-2308-48ff-adb2-33fb0b0741f1",
        "state_id": "1639d8f7-f949-4a23-b93c-9bb96128b54f"
        }
    )

@pytest.mark.asyncio
async def test_reservation_update(SchemaExecutorDemo):
    tableName="facilities_events"
    variables={
        "id": "e622232d-e34d-4efc-8094-74ace62c7989",
        "facility_id": "7dcf3d10-3a41-4c36-9700-99d885a1e474",
        "state_id": "83e7e264-464d-47ce-8ccd-a5b962fdeed4"
    }
    queryRead = getQuery(tableName=tableName, queryName="read")
    queryUpdate = getQuery(tableName=tableName, queryName="update")
    _variables = variables

    variable_values = {**variables}
    variable_values["id"] = variables["facility_id"]
    responseJson = await SchemaExecutorDemo(query=queryRead, variable_values=variable_values)
    responseData = responseJson.get("data")
    assert responseData is not None, f"got no data while asking for lastchange atribute {responseJson}"
    
    [responseEntity, *_] = responseData.values()
    assert responseEntity is not None, f"got no entity while asking for lastchange atribute {responseJson}"
    reservations = responseEntity["reservations"]
    reservation = next(filter(lambda r: r["id"] == variables["id"], reservations), None)
    assert reservation is not None, f"reservation not found {reservations}"
    lastchange = reservation.get("lastchange", None)
    assert lastchange is not None, f"query read for table {tableName} is not asking for lastchange which is needed"
    _variables["lastchange"] = lastchange
    responseJson = await SchemaExecutorDemo(query=queryUpdate, variable_values=_variables)
    assert "errors" not in responseJson, f"update failed {responseJson}"
    logging.info(f"query for {queryUpdate} with {_variables}, no tested response")

    pass

@pytest.mark.asyncio
async def test_reservation_delete(SchemaExecutorDemo):
    tableName="facilities_events"
    variables={
        "id": "e622232d-e34d-4efc-8094-74ace62c7989",
        "facility_id": "7dcf3d10-3a41-4c36-9700-99d885a1e474",
        "state_id": "83e7e264-464d-47ce-8ccd-a5b962fdeed4"
    }
    queryRead = getQuery(tableName=tableName, queryName="read")
    queryDelete = getQuery(tableName=tableName, queryName="delete")
    _variables = variables

    variable_values = {**variables}
    variable_values["id"] = variables["facility_id"]
    responseJson = await SchemaExecutorDemo(query=queryRead, variable_values=variable_values)
    responseData = responseJson.get("data")
    assert responseData is not None, f"got no data while asking for lastchange atribute {responseJson}"
    
    [responseEntity, *_] = responseData.values()
    assert responseEntity is not None, f"got no entity while asking for lastchange atribute {responseJson}"
    reservations = responseEntity["reservations"]
    reservation = next(filter(lambda r: r["id"] == variables["id"], reservations), None)
    assert reservation is not None, f"reservation not found {reservations}"
    lastchange = reservation.get("lastchange", None)
    assert lastchange is not None, f"query read for table {tableName} is not asking for lastchange which is needed"
    _variables["lastchange"] = lastchange
    responseJson = await SchemaExecutorDemo(query=queryDelete, variable_values=_variables)
    assert "errors" not in responseJson, f"update failed {responseJson}"
    logging.info(f"query for {queryDelete} with {_variables}, no tested response")

    pass

text_event_resolve_reference = createTest2(
    tableName="events",
    queryName="resolve_reference",
    variables={
        "id": "a64871f8-2308-48ff-adb2-33fb0b0741f1"
    }
)