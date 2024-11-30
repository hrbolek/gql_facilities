import asyncio
import sqlalchemy
from src.DBDefinitions import startEngine, FacilityModel
from sqlalchemy import select
import functools
import time

mainstmt = select(FacilityModel)

def filter_by_statement(self, names):
    names = names.split(";")
    values = {name: sqlalchemy.bindparam(name) for name in names}
    statement = mainstmt.filter_by(**values)
    compiled = statement.compile()   
    return compiled

filter_by_statement_cached = functools.cache(filter_by_statement)

async def experiment(**kwargs):
    names = ";".join(kwargs.keys())
    start = time.perf_counter()
    for i in range(1000):
        compiled = filter_by_statement(None, names)
    duration = time.perf_counter() - start
    print(f"{duration} for 1000")
    
    start = time.perf_counter()
    for i in range(1000):
        compiled = filter_by_statement(None, names)
    duration = time.perf_counter() - start    
    print(f"{duration} for 1000")

    # print("compiled.bind_names", compiled.bind_names)
@functools.cache
def f(kwargs):
    print(f"called with {kwargs}")
    return kwargs

asyncio.run(experiment(id=5))

# f({"a": 1})
# f({"a": 1})
print({"a": 1} == {"a": 1})

data = {"value": "value"}