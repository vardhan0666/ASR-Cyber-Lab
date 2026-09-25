"""
Reusable, defensive input validation helpers.

These validators are used by Pydantic schemas and services to ensure that
only well-formed identifiers (IP addresses, CIDR ranges, hostnames, plain
names) ever reach the database or, critically, the Nmap subprocess layer.
"""

import ipaddress
import re

from app.core.exceptions import ValidationError

# RFC-1123-ish hostname pattern: labels of 1-63 alphanumerics/hyphens,
# no leading/trailing hyphen, dot-separated, overall <= 253 chars.
_HOSTNAME_REGEX = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))*$"
)

_SAFE_NAME_REGEX = re.compile(r"^[A-Za-z0-9 _.\-]{1,255}$")


def is_valid_ipv4(value: str) -> bool:
    try:
        ipaddress.IPv4Address(value)
        return True
    except ValueError:
        return False


def is_valid_cidr(value: str) -> bool:
    try:
        ipaddress.IPv4Network(value, strict=False)
        return True
    except ValueError:
        return False


def is_valid_hostname(value: str) -> bool:
    if not value or len(value) > 253:
        return False
    return bool(_HOSTNAME_REGEX.match(value))


def validate_target_address(value: str) -> str:
    """Ensure a target address is a plain IPv4 address, an IPv4 CIDR range,
    or a syntactically valid hostname. Raises ValidationError otherwise.

    This is a strict allowlist by design: no shell metacharacters, no
    Nmap flags, no comma/space-separated lists are accepted here."""
    candidate = value.strip()
    if not candidate:
        raise ValidationError("Target address cannot be empty")

    if is_valid_ipv4(candidate) or is_valid_cidr(candidate) or is_valid_hostname(candidate):
        return candidate

    raise ValidationError(
        "Target address must be a valid IPv4 address, IPv4 CIDR range, "
        "or hostname (no additional characters or flags are permitted)."
    )


def validate_name_field(
    value: str, field_name: str = "name", max_length: int = 255
) -> str:
    """Validate a human-readable name/label field (target name, scan name)."""
    candidate = value.strip()
    if not candidate:
        raise ValidationError(f"{field_name} cannot be empty")
    if len(candidate) > max_length:
        raise ValidationError(f"{field_name} must be at most {max_length} characters")
    if not _SAFE_NAME_REGEX.match(candidate):
        raise ValidationError(
            f"{field_name} may only contain letters, numbers, spaces, "
            "underscores, hyphens, and periods"
        )
    return candidate