import pytest_asyncio
import pytest
import logging
import pydantic
import fastapi
import uvicorn
import aiohttp
import asyncio
import time

from contextlib import contextmanager

class Item(pydantic.BaseModel):
    query: str
    variables: dict = None
    operationName: str = None

logging.getLogger("uvicorn.error").setLevel(logging.DEBUG)
log_config = uvicorn.config.LOGGING_CONFIG
log_config["loggers"]["uvicorn"]["level"] = "DEBUG"
log_config["loggers"]["uvicorn.error"]["level"] = "DEBUG"
log_config["loggers"]["uvicorn.access"]["level"] = "DEBUG"

def runGQLServer(port, resolvers):
    logging.info(f"going to runGQLServer {port}")
    
    @contextmanager
    def lifespan():
        logging.info(f"lifespan enter")
        with open("./fastapi.txt", "a", encoding="utf-8") as f:
            f.writelines(["hu"])
        yield
        logging.info(f"lifespan leave")

    app = fastapi.FastAPI(lifespan=lifespan)

    @app.post("/gql")
    async def gql_query(item: Item):
        reactions = (resolver(item) for resolver in resolvers)
        filtered = (reaction for reaction in reactions if reaction is not None)
        first = next(filtered, None)
        logging.info(f"SERVER Query {item} -> {first}")
        return first
    
    logging.info(f"before uvicorn {port}")
    try:
        uvicorn.run(app, port=port, host="0.0.0.0", log_level="debug", log_config=log_config)
    except Exception as e:
        logging.info(f"Exception {e}")    
    logging.info(f"after uvicorn {port}")

@contextmanager
def startGQLServer(port, resolvers):
    #print(response)
    from multiprocessing import Process
    from threading import Thread
    # _api_process = Thread(target=runGQLServer, kwargs={"resolvers": resolvers, "port": port})
    _api_process = Process(target=runGQLServer, daemon=True, kwargs={"resolvers": resolvers, "port": port})
    # _api_process = Process(target=runGQLServer, kwargs={"resolvers": resolvers, "port": port})
    _api_process.start()
    # time.sleep(5)
    print(f"Server started at {port} ({_api_process})")
    logging.info(f"Server started at {port} ({_api_process})")
    yield _api_process
    _api_process.terminate()
    _api_process.join()
    assert _api_process.is_alive() == False, "Server still alive :("
    print(f"Server stopped at {port}")
    logging.info(f"Server stopped at {port}")

serversTestscope = "session"

def serveMe(item: Item):
    logging.info(f"serveMe {item}")
    if "me {" in item.query:
        result = {
            "data": {
                "me": {
                    "id": "51d101a0-81f1-44ca-8366-6cf51432e8d6",
                    "roles": []
                }
            }
        }
        
    else:
        result = None
    return result

@pytest.fixture(autouse=True, scope=serversTestscope)
def NoRole_UG_Server():
    responses = [
        serveMe
    ]

    port = 8129
    url = f"http://localhost:{port}/gql"
    async def client(query, variables):
        payload = {
            "query": query,
            "variables": variables
        }
        logging.info(f"{url} payload {payload}")
        tryAgain = True
        while tryAgain:
            await asyncio.sleep(0)
            tryAgain = False
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as resp:
                        responsetxt = await resp.text()
                        logging.info(f"responsetxt {responsetxt}")

                        assert resp.status == 200, f"{url} bad status during query {query} \n{resp} / {responsetxt}"
                        response = await resp.json()
                        return response
            except Exception as e:
                print("Client Exception", e, type(e), flush=True)
                logging.info(f"Client Exception {e}, {type(e)}")
                # tryAgain = isinstance(e, aiohttp.client_exceptions.ClientConnectorError)
            pass

    # asContext = contextmanager(startGQLServer)
    with startGQLServer(port=port, resolvers=responses) as serverstates:
    # serverstates = startGQLServer(port=port, resolvers=responses)
        # start = next(serverstates)
        # end = next(serverstates, None)
        yield client
        # end = next(serverstates, None)
    pass

@pytest.fixture
def SchemaExecutor():
    # SQLite, Info
    Info = {}
    from src.GraphTypeDefinitions import schema
    async def Execute(query, variable_values={}):
        result = await schema.execute(query=query, variable_values=variable_values, context_value=Info.context)
        value = {"data": result.data} 
        if result.errors:
            value["errors"] = result.errors
        return value
    return Execute
