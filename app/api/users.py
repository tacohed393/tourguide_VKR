from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.models.place import Place
from app.api.auth import get_current_user
from app.schemas.place import PlaceResponse

router = APIRouter()

# Получить профиль + список избранного
@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.id == current_user.id).options(selectinload(User.favorites))
    result = await db.execute(stmt)
    user_with_favs = result.scalars().first()
    
    return {
        "email": user_with_favs.email,
        "id": user_with_favs.id,
        "favorites": user_with_favs.favorites
    }

# Добавить в избранное
@router.post("/favorites/{place_id}")
async def add_favorite(
    place_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    place = await db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    
    stmt = select(User).where(User.id == current_user.id).options(selectinload(User.favorites))
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if place not in user.favorites:
        user.favorites.append(place)
        await db.commit()
        
    return {"status": "added"}


@router.delete("/favorites/{place_id}")
async def remove_favorite(
    place_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.id == current_user.id).options(selectinload(User.favorites))
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    
    user.favorites = [p for p in user.favorites if p.id != place_id]
    await db.commit()
    
    return {"status": "removed"}