import jwt
import pytest
import asyncio

import app.services.auth_service as auth_module
from app.services.auth_service import AuthService


TEST_JWT_SECRET = "unit-test-secret-key-for-hs256-must-be-at-least-32-bytes"

auth_module.SECRET_KEY = TEST_JWT_SECRET


class FakeObjectId:
    def __str__(self):
        return "user-id-123"


class FakeInsertResult:
    inserted_id = FakeObjectId()


class FakeUsersCollection:
    def __init__(self, existing_user=None):
        self.existing_user = existing_user
        self.inserted_document = None
        self.find_one_query = None

    async def find_one(self, query):
        self.find_one_query = query
        return self.existing_user

    async def insert_one(self, document):
        self.inserted_document = document
        return FakeInsertResult()


class FakeUserCreate:
    def __init__(self, email="test@example.com", password="plain-password"):
        self.email = email
        self.password = password

    def model_dump(self):
        return {
            "email": self.email,
            "password": self.password,
            "fullName": "Test User",
        }

    def get_hashed_password(self):
        return "hashed-password"


def test_register_user_success_hashes_password_and_saves_user(monkeypatch):
    fake_collection = FakeUsersCollection(existing_user=None)
    monkeypatch.setattr(auth_module, "users_collection", fake_collection)

    user_data = FakeUserCreate()

    result = asyncio.run(AuthService.register_user(user_data))

    assert fake_collection.find_one_query == {"email": "test@example.com"}
    assert fake_collection.inserted_document is not None
    assert fake_collection.inserted_document["password"] == "hashed-password"
    assert fake_collection.inserted_document["password"] != "plain-password"
    assert "createdAt" in fake_collection.inserted_document

    assert result["id"] == "user-id-123"
    assert result["email"] == "test@example.com"


def test_register_user_duplicate_email_raises_error(monkeypatch):
    fake_collection = FakeUsersCollection(existing_user={"email": "test@example.com"})
    monkeypatch.setattr(auth_module, "users_collection", fake_collection)

    with pytest.raises(ValueError, match="Email already exists"):
        asyncio.run(AuthService.register_user(FakeUserCreate()))


def test_authenticate_user_success_returns_user(monkeypatch):
    fake_user = {
        "_id": FakeObjectId(),
        "email": "test@example.com",
        "password": "hashed-password",
    }
    fake_collection = FakeUsersCollection(existing_user=fake_user)

    monkeypatch.setattr(auth_module, "users_collection", fake_collection)
    monkeypatch.setattr(auth_module, "verify_password", lambda raw, hashed: True)

    result = asyncio.run(
        AuthService.authenticate_user("test@example.com", "plain-password")
    )

    assert fake_collection.find_one_query == {"email": "test@example.com"}
    assert result is not None
    assert result["id"] == "user-id-123"
    assert result["email"] == "test@example.com"


def test_authenticate_user_wrong_email_returns_none(monkeypatch):
    fake_collection = FakeUsersCollection(existing_user=None)
    monkeypatch.setattr(auth_module, "users_collection", fake_collection)

    result = asyncio.run(
        AuthService.authenticate_user("missing@example.com", "plain-password")
    )

    assert result is None


def test_authenticate_user_wrong_password_returns_none(monkeypatch):
    fake_user = {
        "_id": FakeObjectId(),
        "email": "test@example.com",
        "password": "hashed-password",
    }
    fake_collection = FakeUsersCollection(existing_user=fake_user)

    monkeypatch.setattr(auth_module, "users_collection", fake_collection)
    monkeypatch.setattr(auth_module, "verify_password", lambda raw, hashed: False)

    result = asyncio.run(
        AuthService.authenticate_user("test@example.com", "wrong-password")
    )

    assert result is None


def test_create_access_token_contains_payload_and_expiration():
    token = AuthService.create_access_token(
        {
            "sub": "user-id-123",
            "email": "test@example.com",
        }
    )

    decoded = jwt.decode(
        token,
        auth_module.SECRET_KEY,
        algorithms=[auth_module.ALGORITHM],
    )

    assert decoded["sub"] == "user-id-123"
    assert decoded["email"] == "test@example.com"
    assert "exp" in decoded
