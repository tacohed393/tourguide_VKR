from pydantic import BaseModel
from typing import Optional

# --- Базовые схемы ---

class PlaceCreate(BaseModel):
    name: str
    city: str
    type: str
    price: str  
    description: str

class PlaceResponse(BaseModel):
    id: int
    name: str
    city: str
    type: str
    price: str | None = None  
    description: str
    search_context: str | None = None
    image_url: str | None = None
    lat: float | None = None  
    lon: float | None = None  

    class Config:
        from_attributes = True

# --- Схемы для поиска ---

class SearchRequest(BaseModel):
    query: str              
    city: str | None = None 
    limit: int = 2       

class FilterRequest(BaseModel):
    city: str
    type: str | None = None
    price: str | None = None
    limit: int = 2  