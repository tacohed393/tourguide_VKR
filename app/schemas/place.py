from pydantic import BaseModel

class PlaceCreate(BaseModel):
    name: str
    city: str
    type: str
    description: str

class PlaceResponse(BaseModel):
    id: int
    name: str
    city: str
    type: str
    description: str
    search_context: str | None = None

    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    query: str              
    city: str | None = None 
    limit: int = 1          