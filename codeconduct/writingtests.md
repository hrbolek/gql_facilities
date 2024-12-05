## Manual tests
- to run the app the user:
    1. must have running docker compose stack (see docker-compose.data.yml at https://github.com/hrbolek/_uois)
    2. user must be logged in, the landing page is available at http://localhost:33001/
    3. from terminal it is possible to use command `uvicorn main:app --env-file environment.txt --port 8001`
    4. to open web it is common to follow link http://localhost:8001/gql where graphiql interface is
    5. to show the structure of the endpoint there is implemented FastAPI endpoint /voyager see "Voyager"


## The test suite
- Test suite is based on pytest library which can handle asynchronous functions.
- The database which is filled from systemdata.json is sqlite. For the test it is stored in memory
- Tests can be stored in `./tests/gqls/` directory. Often there is one file `test_queries.py` which contains all tests
- For running tests the command `pytest --cov-report term-missing --cov=src --log-cli-level=INFO -x` can be used. 

## Test functions
There are directory structure ./test/gqls which has subdirectories named as tables. 
Each has several files with extension ".gql".
That files contains queries.
That queries can be used in different languages python and javascript included.
It must be consider that in standard setup the strawberry converts resolver names from snake_case into CamelCase.
That has impact on graphQL queries definition.

## Example of test creation
There are prepared functions 
- createByIdTest2 which mainly creates a test based on query _by_id but can be used for any test which expect result in scalar form
- createUpdateTest2 which create an entity, reads lastchange and other attributes with _by_id query, combine the result with parameter variables and performs update mutation
- createDeleteTest2 which create an entity, reads lastchange and other attributes with _by_id query, combine the result with parameter variables and performs delete mutation
- createTest2 is general purpose single stage query to graphql endpoint

Parameter `tablename` must be always provided as it define the location of query.
Parameter `queryname` can be ommited and then it is derived:
- createByIdTest2 use `queryname="read"`
- createUpdateTest2 use `queryname="update"`
- createDeleteTest2 use `queryname="delete"`

Parameter variables can be ommited and then it can be retrieved from file in same directory as query with extension `.var.json`.
If there exists file with extension `.res.json` it is used to test response from particular query.

```python
test_facility_by_id = createByIdTest2(tableName="facilities")
test_facility_update = createUpdateTest2(tableName="facilities", variables={"name": "newname"})
test_facility_create = createTest2(tableName="facilities", queryName="create", variables={"name": "newname"})
test_facility_delete = createDeleteTest2(tableName="facilities", variables={"id": "18375c23-767c-4c1e-adb6-9b2beb463533", "name": "newname"})

test_facility_coverage = createByIdTest2(tableName="facilities", queryName="coverage")
```

## Query and json retrieval
there are functions for that tasks:

```python
import os 
import re
dir_path = os.path.dirname(os.path.realpath(__file__))
print("dir_path", dir_path, flush=True)

location = "./src/tests/gqls"
location = re.sub(r"\\tests\\.+", r"\\tests\\gqls", dir_path)
# location
print("location", location, flush=True)
logging.info(f"Queries location {dir_path} => {location}")
def getQuery(tableName, queryName):
    queryFileName = f"{location}/{tableName}/{queryName}.gql"
    assert os.path.isfile(queryFileName), f"unable find query {queryName}@{tableName} {queryFileName}"
    logging.info(f"found query {queryName}@{tableName} {queryFileName}")
    with open(queryFileName, "r", encoding="utf-8") as f:
        query = f.read()
    return query

def getVariables(tableName, queryName):
    variableFileName = f"{location}/{tableName}/{queryName}.var.json"

    if os.path.isfile(variableFileName):
        with open(variableFileName, "r", encoding="utf-8") as f:
            variables = json.load(f)
    else:
        variables = {}
    return variables

def getExpectedResult(tableName, queryName):
    resultFileName = f"{location}/{tableName}/{queryName}.res.json"

    if os.path.isfile(resultFileName):
        with open(resultFileName, "r", encoding="utf-8") as f:
            expectedResult = json.load(f)
    else:
        expectedResult = None
    return expectedResult
```

## Voyager
voyager is visialiser of graphql endpoint. To include it into app it is needed to add to main.py file next code

```python
@app.get("/voyager", response_class=FileResponse)
async def graphiql():
    realpath = os.path.realpath("./voyager.html")
    return realpath
```

the function return filename where voyager.html is stored, this file can be get from https://github.com/hrbolek/gql_facilities/blob/latest/voyager.html 
