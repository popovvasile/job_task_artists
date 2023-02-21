import logging
from datetime import datetime

from fastapi_utils.tasks import repeat_every

from . import schemas, models
from fastapi import HTTPException, status, APIRouter, Response

from .config import Config
from .services.artist import ArtistsService
from .session import session

router = APIRouter()


@router.on_event("startup")
@repeat_every(seconds=Config().FREQUENCY, raise_exceptions=True, wait_first=True)
async def fetch_artists_task():
    token = ArtistsService(session).get_spotify_token()
    if not token:
        raise Exception("No spotify token found.")

    artist_ids = await ArtistsService(session).get_unchanged_artist_ids()
    for artist in ArtistsService(session).fetch_artists(artist_ids, token):
        if artist and artist.get("id"):
            await ArtistsService(session).write_artist(artist, edited=datetime.now())
    logging.info("Finished fetching artists")


@router.get('/')
def get_artists(limit: int = 10, page: int = 1, search: str = ''):
    skip = (page - 1) * limit

    artists = session.query(models.Artist).filter(
        models.Artist.title.contains(search)).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(artists), 'artists': artists}


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_artist(payload: schemas.ArtistBaseSchema):
    new_artist = models.Artist(**payload.dict())
    session.add(new_artist)
    session.commit()
    session.refresh(new_artist)
    return {"status": "success", "artist": new_artist}


@router.patch('/{artistId}')
def update_artist(artistId: str, payload: schemas.ArtistBaseSchema):
    artist_query = session.query(models.Artist).filter(models.Artist.spotify_id == artistId)
    db_artist = artist_query.first()

    if not db_artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No artist with this id: {artistId} found')
    update_data = payload.dict(exclude_unset=True)
    artist_query.filter(models.Artist.spotify_id == artistId).update(update_data,
                                                       synchronize_session=False)
    session.commit()
    session.refresh(db_artist)
    return {"status": "success", "artist": db_artist}


@router.get('/{artistId}')
def get_post(artistId: str):
    artist = session.query(models.Artist).filter(models.Artist.spotify_id == artistId).first()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No artist with this id: {id} found")
    return {"status": "success", "artist": artist}


@router.delete('/{artistId}')
def delete_post(artistId: str):
    artist_query = session.query(models.Artist).filter(models.Artist.spotify_id == artistId)
    artist = artist_query.first()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No artist with this id: {id} found')
    artist_query.delete(synchronize_session=False)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
