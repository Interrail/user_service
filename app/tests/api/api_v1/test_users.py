from typing import Dict

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud, schemas
from app.core.config import settings
from app.schemas import UserCreate
from app.schemas.user import RoleEnum
from app.tests.utils.utils import random_email, random_lower_string


def test_get_all_users(client, test_users, superuser_token_headers):
    response = client.get(f"{settings.API_V1_STR}/users", headers=superuser_token_headers)

    def validate(user):
        return schemas.User(**user)

    users_map = map(validate, response.json())
    user_list = list(users_map)
    assert len(user_list) == len(test_users)
    assert response.status_code == 200


def test_get_users_superuser_me(test_users, client: TestClient, superuser_token_headers) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["role"] == RoleEnum.admin
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(
        client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["role"] != RoleEnum.admin


def test_create_user_new_email(
        client: TestClient, superuser_token_headers: dict
        , session: Session) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = crud.user.get_by_email(session, email=username)
    assert user
    assert user.email == created_user["email"]


@pytest.mark.parametrize("email,password,role", [
    ("test11@gmail.com", "password1233", RoleEnum.client),
    ("test21@gmail.com", "password1233", RoleEnum.contractor),
    ("test31@gmail.com", "password1233", RoleEnum.admin),
    ("test41@gmail.com", "password1233", RoleEnum.staff),
])
def test_get_existing_user_with_all_types(
        client: TestClient, test_users, superuser_token_headers: dict, session: Session, email, password, role) -> None:
    user_in = UserCreate(email=email, password=password, role=role)
    user = crud.user.create(session, obj_in=user_in)
    user_id = user.id
    r = client.get(
        f"{settings.API_V1_STR}/users/{user_id}", headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.user.get_by_email(session, email=email)
    assert existing_user
    assert existing_user.email == api_user["email"]
    assert existing_user.role == role


def test_create_user_by_normal_user(
        client: TestClient, test_users, normal_user_token_headers: Dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers, json=data,
    )
    assert r.status_code == 200


def test_retrieve_users(
        client: TestClient, superuser_token_headers: dict, session: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    crud.user.create(session, obj_in=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    crud.user.create(session, obj_in=user_in2)

    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item


def test_delete_users(client: TestClient, test_users, superuser_token_headers: dict, session: Session):
    r = client.delete(f"{settings.API_V1_STR}/users/delete/{test_users[1].id}", headers=superuser_token_headers)
    assert r.status_code == 204
