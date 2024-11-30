import os
from uoishelpers.feeders import ImportModels
from uoishelpers.dataloaders import readJsonFile

from src.DBDefinitions import (
    FacilityTypeModel,
    FacilityModel,
    EventFacilityStateType,
    EventFacilityModel
)

def get_demodata(filename="./systemdata.json"):
    return readJsonFile(filename)

async def initDB(asyncSessionMaker, filename="./systemdata.json"):

    dbModels = [
        FacilityTypeModel,
        EventFacilityStateType,
    ]

    DEMODATA = os.environ.get("DEMODATA", None) in ["True", "true"]    
    if DEMODATA:
        dbModels.extend([
            FacilityModel,
            EventFacilityModel        
            ])
        
    jsonData = get_demodata(filename=filename)
    await ImportModels(asyncSessionMaker, dbModels, jsonData)
    pass