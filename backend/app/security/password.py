"""
Password hashing utilities using bcrypt via passlib.

bcrypt is pinned to 4.0.1 in requirements.txt to avoid a known
incompatibility between passlib 1.7.4's version-detection code and
bcrypt >= 4.1 (which removed the `__about__` attribute passlib probes for).
"""

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage. Never store plaintext passwords."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    return _pwd_context.verify(plain_password, hashed_password)