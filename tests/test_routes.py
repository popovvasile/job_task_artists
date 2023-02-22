from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_artist():
    artist_data = {
        "title": "Test Artist",
        "spotify_id": "abc123",
        "genres": ["rock", "pop"],
        "popularity": 50,
    }
    response = client.post("/api/artists", json=artist_data)
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert response.json()["artist"]["title"] == "Test Artist"
    assert response.json()["artist"]["spotify_id"] == "abc123"
    assert response.json()["artist"]["genres"] == ["rock", "pop"]
    assert response.json()["artist"]["popularity"] == 50


def test_update_artist():
    artist_data = {
        "title": "Test Artist",
        "spotify_id": "abc123",
        "genres": ["rock", "pop"],
        "popularity": 50,
    }
    client.post("/api/artists", json=artist_data)

    updated_artist_data = {
        "title": "Updated Artist",
        "genres": ["pop"],
    }
    response = client.patch(f'/api/artists/{artist_data["spotify_id"]}', json=updated_artist_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["artist"]["title"] == "Updated Artist"
    assert response.json()["artist"]["spotify_id"] == "abc123"
    assert response.json()["artist"]["genres"] == ["pop"]
    assert response.json()["artist"]["popularity"] == 50


def test_get_artist():
    artist_data = {
        "title": "Test Artist",
        "spotify_id": "abc123",
        "genres": ["rock", "pop"],
        "popularity": 50,
    }
    client.post("/api/artists", json=artist_data)

    response = client.get(f'/api/artists/{artist_data["spotify_id"]}')
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["artist"]["title"] == "Test Artist"
    assert response.json()["artist"]["spotify_id"] == "abc123"
    assert response.json()["artist"]["genres"] == ["rock", "pop"]
    assert response.json()["artist"]["popularity"] == 50


def test_delete_artist():
    artist_data = {
        "title": "Test Artist",
        "spotify_id": "abc123",
        "genres": ["rock", "pop"],
        "popularity": 50,
    }
    client.post(f'/api/artists/{artist_data["spotify_id"]}', json=artist_data)

    response = client.delete(f'/api/artists/{artist_data["spotify_id"]}')
    assert response.status_code == 204

    response = client.get(f'/api/artists/{artist_data["spotify_id"]}')
    assert response.status_code == 404