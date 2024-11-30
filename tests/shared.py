import sqlalchemy
import asyncio
import pytest

async def prepare_in_memory_sqllite():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    from src.DBDefinitions import BaseModel

    asyncEngine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # asyncEngine = create_async_engine("sqlite+aiosqlite:///data.sqlite")
    async with asyncEngine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    async_session_maker = sessionmaker(
        asyncEngine, expire_on_commit=False, class_=AsyncSession
    )

    return async_session_maker


async def prepare_demodata(async_session_maker):
    from src.DBFeeder import get_demodata
    from src.DBDefinitions import FacilityModel, FacilityTypeModel
    from src.DBDefinitions import EventFacilityModel, EventFacilityStateType

    data = get_demodata()

    from uoishelpers.feeders import ImportModels

    await ImportModels(
        async_session_maker,
        [
            FacilityModel, 
            FacilityTypeModel,
            EventFacilityModel, 
            EventFacilityStateType,            
        ],
        data,
    )


async def createContext(asyncSessionMaker):
    from Dataloaders import createLoaders_3
    return {
        "asyncSessionMaker": asyncSessionMaker,
        "all": await createLoaders_3(asyncSessionMaker),
    }
