from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.place import Place
from app.schemas.place import PlaceCreate, PlaceResponse, SearchRequest, FilterRequest
from app.services.ml_service import get_embedding
from typing import Optional



router = APIRouter()

@router.post("/", response_model=PlaceResponse)
async def create_place(place_in: PlaceCreate, db: AsyncSession = Depends(get_db)):
    """Добавить новое место в базу (автоматически векторизует описание)""" #для сваги

    text_to_embed = place_in.search_context if place_in.search_context else place_in.description

    # vector = get_embedding(place_in.description)
    vector = await get_embedding(text_to_embed)
    
    new_place = Place(
        name=place_in.name,
        city=place_in.city,
        type=place_in.type,
        description=place_in.description,
        search_context=text_to_embed,
        embedding=vector
    )
    
    db.add(new_place)
    await db.commit()
    await db.refresh(new_place)
    return new_place

SEARCH_THRESHOLD = 1.052   

@router.post("/search/ai", response_model=list[PlaceResponse])
async def search_places(search_in: SearchRequest, db: AsyncSession = Depends(get_db)):
    """Гибридный поиск: Фильтр SQL + Векторная близость""" #для сваги
    
    # query_vector = get_embedding(search_in.query)
    query_vector = await get_embedding(search_in.query)

    distance_col = Place.embedding.l2_distance(query_vector).label("distance")
    
    stmt = select(Place, distance_col)
    
    if search_in.city:
        stmt = stmt.where(Place.city == search_in.city)
    
    
    stmt = stmt.order_by(distance_col).limit(search_in.limit)
    
    result = await db.execute(stmt)
    rows = result.all() 

    found_places = []
    
    print(f"--- SEARCH DEBUG: '{search_in.query}' ---")
    for place, dist in rows:
        print(f"Candidate: {place.name}, Dist: {dist}")

        if dist < SEARCH_THRESHOLD:
            found_places.append(place)
        else:
            print(f"-> Skipped '{place.name}' (too far)")

    return found_places

@router.post("/search/filters", response_model=list[PlaceResponse])
async def search_by_filters(
    search_in: FilterRequest, 
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Place)
    stmt = stmt.where(Place.city == search_in.city)

    if search_in.type:
        stmt = stmt.where(Place.type == search_in.type)
        
    if search_in.price:
        stmt = stmt.where(Place.price == search_in.price)
    
    stmt = stmt.limit(search_in.limit)
    result = await db.execute(stmt)
    return result.scalars().all()