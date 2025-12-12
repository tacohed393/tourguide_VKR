from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    city: Mapped[str] = mapped_column(String, index=True) 
    type: Mapped[str] = mapped_column(String)  

    
    description: Mapped[str] = mapped_column(Text) 
    search_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    embedding: Mapped[list[float]] = mapped_column(Vector(768))

    def __repr__(self):
        return f"<Place {self.name} ({self.city})>"