from typing import List, Optional
from pydantic import BaseModel


class ArtistBaseSchema(BaseModel):
    spotify_id: str
    popularity: Optional[str]
    name: Optional[str]
    genres: Optional[List[str]]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListArtistResponse(BaseModel):
    status: str
    results: int
    artists: List[ArtistBaseSchema]
