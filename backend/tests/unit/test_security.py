"""Unit tests for JWT security and password hashing."""

import time
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Test bcrypt password hashing and verification."""

    def test_hash_is_not_plaintext(self) -> None:
        """Hashed password should not equal the original."""
        pw = "SecurePass1"
        assert hash_password(pw) != pw

    def test_verify_correct_password(self) -> None:
        """Correct password should verify successfully."""
        pw = "SecurePass1"
        hashed = hash_password(pw)
        assert verify_password(pw, hashed) is True

    def test_verify_wrong_password(self) -> None:
        """Wrong password should fail verification."""
        hashed = hash_password("SecurePass1")
        assert verify_password("WrongPass1", hashed) is False

    def test_different_hashes_same_password(self) -> None:
        """bcrypt salting produces different hashes for the same password."""
        pw = "SecurePass1"
        assert hash_password(pw) != hash_password(pw)


class TestJWT:
    """Test JWT token creation and validation."""

    def test_access_token_decode(self) -> None:
        """Access token should decode with correct claims."""
        user_id = str(uuid.uuid4())
        token = create_access_token(user_id)
        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "jti" in payload

    def test_refresh_token_decode(self) -> None:
        """Refresh token should decode with type='refresh'."""
        user_id = str(uuid.uuid4())
        token = create_refresh_token(user_id)
        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_tampered_token_raises(self) -> None:
        """Modified token should raise on decode."""
        from jose import JWTError

        token = create_access_token(str(uuid.uuid4()))
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(JWTError):
            decode_token(tampered)

    def test_expired_token_raises(self) -> None:
        """Expired token should raise JWTError."""
        from jose import JWTError

        settings = get_settings()
        payload = {
            "sub": str(uuid.uuid4()),
            "jti": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        }
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithm=settings.JWT_ALGORITHM,
        )
        with pytest.raises(JWTError):
            decode_token(token)

    def test_custom_jti(self) -> None:
        """Custom JTI should be preserved in the token."""
        jti = str(uuid.uuid4())
        token = create_access_token(str(uuid.uuid4()), jti=jti)
        payload = decode_token(token)
        assert payload["jti"] == jti
