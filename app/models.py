from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ARRAY
from app.session import Base


class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    spotify_id = Column(String, nullable=True, unique=True)
    name = Column(String, index=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    edited = Column(DateTime, nullable=True)
    popularity = Column(Integer, nullable=True)
    genres = Column(ARRAY(String), nullable=True)

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda x: x.isoformat(" ")}