from fastapi import status
from core.settings import Settings
from tools import film_uuid, user_uuid
from constants import LIKE_RATING_HIGH, LIKE_RATING_AVG, FILM_ID, USER_ID, LIKE_VALUE

settings = Settings()

def test_create_like(auth_client):
    response = auth_client.post("/api/v1/like/", json={
    FILM_ID: film_uuid,
    LIKE_VALUE: LIKE_RATING_HIGH
})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get(LIKE_VALUE) == LIKE_RATING_HIGH
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid

    response = auth_client.post("/api/v1/like/", json={
        FILM_ID: film_uuid,
        LIKE_VALUE: LIKE_RATING_HIGH
    })
    assert response.status_code == status.HTTP_409_CONFLICT

def test_get_like(auth_client):
    response = auth_client.get(f"/api/v1/like/{film_uuid}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get(LIKE_VALUE) == LIKE_RATING_HIGH
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid

def test_patch_like(auth_client):
    response = auth_client.patch("/api/v1/like/", json={
    FILM_ID: film_uuid,
    LIKE_VALUE: LIKE_RATING_AVG
})
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get(LIKE_VALUE) == LIKE_RATING_AVG
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid


def test_get_after_patch_like(auth_client):
    response = auth_client.get(f"/api/v1/like/{film_uuid}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get(LIKE_VALUE) == LIKE_RATING_AVG
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid


def test_delete_like(auth_client):
    response = auth_client.delete(f"/api/v1/like/{film_uuid}")
    assert response.status_code == status.HTTP_200_OK

    response = auth_client.delete(f"/api/v1/like/{film_uuid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND