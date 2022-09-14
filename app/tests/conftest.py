import pytest

from typing import Dict, Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import models
from app.api.deps import get_db
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.session import SessionLocal
from app.main import app
from app.schemas.user import RoleEnum
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:5432/{settings.POSTGRES_DB}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_users(session):
    users_data = [
        {"email": settings.FIRST_SUPERUSER, "hashed_password": get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
         "role": RoleEnum.admin},
        {"email": "test1@gmail.com", "hashed_password": get_password_hash("test123"), "role": RoleEnum.client},
        {"email": "test2@gmail.com", "hashed_password": get_password_hash("test123"), "role": RoleEnum.staff},
        {"email": "test23@gmail.com", "hashed_password": get_password_hash("test123"), "role": RoleEnum.contractor}
    ]

    def create_user_model(users):
        return models.User(**users)

    users = list(map(create_user_model, users_data))
    session.add_all(users)
    session.commit()
    users = session.query(models.User).all()
    return users


# @pytest.fixture(scope="session")
# def db() -> Generator:
#     yield SessionLocal()
#
#
# @pytest.fixture(scope="module")
# def client() -> Generator:
#     with TestClient(app) as c:
#         yield c


@pytest.fixture
def superuser_token_headers(client: TestClient, test_users) -> Dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture
def normal_user_token_headers(client: TestClient, test_users) -> str:
    login_data = {
        "username": "test1@gmail.com",
        "password": "test123"
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
