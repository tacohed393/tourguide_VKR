from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles 

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.core.database import engine, Base
from app.api.places import router as places_router
from app.models.place import Place 

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # ВОТ ЭТА СТРОКА ДОЛЖНА БЫТЬ АКТИВНА:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # эта не нужна с миграцией
        # await conn.run_sync(Base.metadata.create_all)
        
    print("База данных готова и векторы включены!")
    yield

app = FastAPI(title="VKR TourGuide API")
app.mount("/static", StaticFiles(directory="static"), name="static")
#все разрешено, ничего не запрещено
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
#Руты
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(places_router, prefix="/places", tags=["Places"])

@app.get("/")
async def root():
    return {"message": "API работает! Перейди на /docs для тестирования."}