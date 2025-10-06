"""Password hashing helpers shared across the application."""

from __future__ import annotations

from passlib.context import CryptContext


_pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validate a plain password against a stored hash."""

    if not hashed_password:
        return False
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        # Raised when hash format is unknown — treat as failed verification.
        return False


def hash_password(password: str) -> str:
    """Hash a password using the configured context."""

    return _pwd_context.hash(password)

