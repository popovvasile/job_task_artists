import logging
from datetime import datetime

from fastapi_utils.tasks import repeat_every

from fastapi import HTTPException, status, APIRouter, Response

from models.artist import Artist
from config import Config
from schemas.schemas import ArtistBaseSchema
from services.artist import ArtistsService
from sessions.session import LocalSession

router = APIRouter()


@router.on_event("startup")
@repeat_every(seconds=Config().FREQUENCY, raise_exceptions=True, wait_first=True)
def fetch_artists_task():
    token = ArtistsService(LocalSession()).get_spotify_token()
    if not token:
        raise Exception("No spotify token found.")

    artist_ids = ArtistsService(LocalSession()).get_unchanged_artist_ids()
    for artist in ArtistsService(LocalSession()).fetch_artists(artist_ids, token):
        if artist and artist.get("id"):
            ArtistsService(LocalSession()).write_artist(artist, edited=datetime.now())
    logging.info("Finished fetching artists")


@router.get('/')
def get_artists(limit: int = 10, page: int = 1, search: str = ''):
    skip = (page - 1) * limit

    artists = LocalSession().query(Artist).filter(
        Artist.title.contains(search)).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(artists), 'artists': artists}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_artist(payload: ArtistBaseSchema):
    new_artist = Artist(**payload.dict())
    LocalSession().add(new_artist)
    LocalSession().commit()
    return {"status": "success", "artist": new_artist}


@router.patch('/{artistId}')
def update_artist(artistId: str, payload: ArtistBaseSchema):
    artist_query = LocalSession().query(Artist).filter(Artist.spotify_id == artistId)
    db_artist = artist_query.first()

    if not db_artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No artist with this id: {artistId} found')
    update_data = payload.dict(exclude_unset=True)
    artist_query.filter(Artist.spotify_id == artistId).update(update_data,
                                                              synchronize_session=False)
    LocalSession().commit()
    return {"status": "success", "artist": db_artist}


@router.get('/{artistId}')
def get_post(artistId: str):
    artist = LocalSession().query(Artist).filter(Artist.spotify_id == artistId).first()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No artist with this id: {id} found")
    return {"status": "success", "artist": artist}


@router.delete('/{artistId}')
def delete_post(artistId: str):
    artist_query = LocalSession().query(Artist).filter(Artist.spotify_id == artistId)
    artist = artist_query.first()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No artist with this id: {id} found')
    artist_query.delete(synchronize_session=False)
    LocalSession().commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
