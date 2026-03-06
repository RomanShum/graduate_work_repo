from fastapi import status
from core.settings import Settings
from tools import film_uuid, user_uuid
from constants import USER_ID, FILM_ID

settings = Settings()

def test_create_favorite(auth_client):
    response = auth_client.put("/api/v1/favorite/", json={
    FILM_ID: film_uuid
})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid

    response = auth_client.put("/api/v1/favorite/", json={
        FILM_ID: film_uuid
    })
    assert response.status_code == status.HTTP_409_CONFLICT

def test_get_favorite(auth_client):
    response = auth_client.get("/api/v1/favorite/{film_uuid}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid


def test_delete_favorite(auth_client):
    response = auth_client.delete(f"/api/v1/favorite/{film_uuid}")
    assert response.status_code == status.HTTP_200_OK

    response = auth_client.delete(f"/api/v1/favorite/{film_uuid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND