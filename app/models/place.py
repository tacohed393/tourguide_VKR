from sqlalchemy import String, Integer, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    city: Mapped[str] = mapped_column(String, index=True) 
    type: Mapped[str] = mapped_column(String)  

    #lat: Mapped[float] = mapped_column(Float, nullable=True)
    #lon: Mapped[float] = mapped_column(Float, nullable=True)

    image_url: Mapped[str] = mapped_column(String, nullable=True)

    price: Mapped[str] = mapped_column(String, nullable=True) 

    
    description: Mapped[str] = mapped_column(Text) 
    search_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    embedding: Mapped[list[float]] = mapped_column(Vector(768))

    def __repr__(self):
        return f"<Place {self.name} ({self.city})>"