from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ArtistBaseSchema(BaseModel):
    id: int = Field(..., description="ID")
    spotify_id: Optional[str] = Field(None, description="Spotify ID")
    name: str = Field(..., description="Name")
    created: datetime = Field(..., description="Created")
    updated: datetime = Field(..., description="Updated")
    edited: Optional[datetime] = Field(None, description="Edited")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListArtistResponse(BaseModel):
    status: str
    results: int
    artists: List[ArtistBaseSchema]
