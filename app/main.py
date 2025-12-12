from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import engine, Base
from app.api.places import router as places_router
from app.models.place import Place 

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    print("База данных готова!")
    yield

app = FastAPI(title="VKR TourGuide API", lifespan=lifespan)

#все разрешено, ничего не запрещено
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(places_router, prefix="/places", tags=["Places"])

@app.get("/")
async def root():
    return {"message": "API работает! Перейди на /docs для тестирования."}