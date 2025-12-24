from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.models.place import Place
from app.api.auth import get_current_user
from app.schemas.place import PlaceResponse
from app.core.security import verify_password, get_password_hash
from app.schemas.user import UserUpdate, UserResponse 
from sqlalchemy.future import select as select_future
from app.schemas.user import UserResponse 

router = APIRouter()

# Получить профиль + список избранного
@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.favorites)
        )
    )
    result = await db.execute(stmt)
    
    user_with_favs = result.scalars().unique().first() 
    
    if not user_with_favs:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "email": user_with_favs.email,
        "id": user_with_favs.id,
        "username": user_with_favs.username,
        "favorites": [
            
            PlaceResponse.model_validate(place).model_dump()
            for place in user_with_favs.favorites
        ]
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

# Обновление профиля
@router.put("/me/update", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user_update.old_password or user_update.new_password:
        if not user_update.old_password or not user_update.new_password:
            raise HTTPException(status_code=400, detail="Для смены пароля нужны оба поля: старый и новый.")
        
        if not verify_password(user_update.old_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Старый пароль неверен.")
        
        current_user.hashed_password = get_password_hash(user_update.new_password)
     
    if user_update.username:
        current_user.username = user_update.username
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return current_user