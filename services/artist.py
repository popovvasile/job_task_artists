import os
from datetime import datetime
from typing import Optional, List, Union

import httpx as httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import Config
from models.artist import Artist
# from app.standalone_session import standalone_session
from utils.db_utils import Transactional


class ArtistsService:
    def __init__(self, session):
        self.session = session()

    def get_spotify_token(self) -> str:
        url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": Config().SPOTIFY_CLIENT_ID,
            "client_secret": Config().SPOTIFY_CLIENT_SECRET,
        }
        response = httpx.post(url=url, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def get_unchanged_artist_ids(self):
        sql = """
                SELECT spotify_id FROM artists
                WHERE edited IS NULL AND spotify_id IS NOT NULL
            """
        result = self.session.execute(sql)
        return result.scalars().all()

    def get_artist_by_id(
            self, id: str
    ) -> Artist:
        artist = self.session.execute(select(Artist).where(Artist.spotify_id==id))
        return artist.first()[0]

    @Transactional()
    def write_artist(self, artist: dict, edited=None):
        if not artist["id"]:
            raise Exception("Spotify ID missing")
        existing_artist = self.get_artist_by_id(artist["id"])

        if existing_artist:
            existing_artist.name = artist["name"]
            existing_artist.genres = artist["genres"]
            existing_artist.popularity = artist["popularity"]
            existing_artist.from_spotify = edited
            existing_artist.updated_at = datetime.now()
            self.session.add(existing_artist)
        else:
            db_artist = Artist(spotify_id=artist["id"],
                               name=artist["name"],
                               genres=str(artist["genres"]),
                               popularity=artist["popularity"])
            self.session.add(db_artist)

        return

    def fetch_artists(self, artist_ids: List[str], token: str) -> list:
        url = f"https://api.spotify.com/v1/artists"
        params = {"ids": ",".join(artist_ids)}
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        response = httpx.get(url=url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()["artists"]

    def get_artist_list(
            self,
            limit: int = 10,
            prev: Optional[int] = None,
    ) -> List[Artist]:
        query = select(Artist)

        if prev:
            query = query.where(Artist.id < prev)

        if limit > 10:
            limit = 10

        query = query.limit(limit)
        result = self.session.execute(query)
        return result.scalars().all()

    @Transactional()
    def create_artist(
            self, name: str, spotify_id: str
    ) -> Artist:
        artist = Artist(name=name, spotify_id=spotify_id)
        self.session.add(artist)
        return artist

    @Transactional()
    def update_artist(
            self, name: str, spotify_id: str
    ) -> None:
        artist = self.session.execute(select(Artist).where(Artist.spotify_id == spotify_id))
        if not artist.from_spotify:
            artist.name = name
            artist.updated = datetime.now()
            self.session.add(artist)

    @Transactional()
    def delete_artist(
            self, spotify_id: str
    ) -> None:
        artist = self.session.execute(select(Artist).where(Artist.spotify_id == spotify_id))
        self.session.delete(artist.first())

    def get_artist(
            self, spotify_id: str
    ) -> None:
        artist = self.session.execute(select(Artist).where(Artist.spotify_id == spotify_id))
        return artist.first()
