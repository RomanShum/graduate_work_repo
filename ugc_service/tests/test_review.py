from fastapi import status
from core.settings import Settings
from tools import film_uuid, user_uuid
from constants import REVIEW_VALUE_TEST, REVIEW_VALUE_TEST1, USER_ID, FILM_ID, REVIEW_VALUE

settings = Settings()

def test_create_review(auth_client):
    response = auth_client.post("/api/v1/review/", json={
    FILM_ID: film_uuid,
    REVIEW_VALUE: REVIEW_VALUE_TEST
})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get(REVIEW_VALUE) == REVIEW_VALUE_TEST
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid

    response = auth_client.post("/api/v1/review/", json={
        FILM_ID: film_uuid,
        REVIEW_VALUE: REVIEW_VALUE_TEST
    })
    assert response.status_code == status.HTTP_409_CONFLICT

def test_get_review(auth_client):
    response = auth_client.get(f"/api/v1/review/{film_uuid}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get(REVIEW_VALUE) == REVIEW_VALUE_TEST
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid

def test_patch_review(auth_client):
    response = auth_client.patch("/api/v1/review/", json={
    FILM_ID: film_uuid,
    REVIEW_VALUE: REVIEW_VALUE_TEST1
})
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get(REVIEW_VALUE) == REVIEW_VALUE_TEST1
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid

def test_get_after_patch_review(auth_client):
    response = auth_client.get(f"/api/v1/review/{film_uuid}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get(REVIEW_VALUE) == REVIEW_VALUE_TEST1
    assert response.json().get(USER_ID) == user_uuid
    assert response.json().get(FILM_ID) == film_uuid


def test_delete_review(auth_client):
    response = auth_client.delete(f"/api/v1/review/{film_uuid}")
    assert response.status_code == status.HTTP_200_OK

    response = auth_client.delete(f"/api/v1/review/{film_uuid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND