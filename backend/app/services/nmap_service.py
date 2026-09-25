"""
Safe, validated Nmap subprocess execution.

CRITICAL SECURITY INVARIANTS:
  - Nmap is invoked via subprocess.run() with a LIST of arguments and
    shell=False. Raw shell strings are never constructed from user input.
  - The only user-influenced value that reaches the subprocess call is the
    target address, and it is validated immediately before use via
    app.core.validators.validate_target_address, which enforces a strict
    IPv4 / IPv4-CIDR / hostname allowlist. That regex/ipaddress-based
    validation structurally guarantees the value can never begin with '-'
    or contain shell metacharacters, so it can never be interpreted as an
    additional Nmap flag.
  - Scan "profiles" are fixed, server-defined argument lists (see
    NMAP_PROFILES below). Callers select a profile by ENUM VALUE only —
    arbitrary Nmap flags can never be supplied by a client.
"""

import logging
import subprocess
from typing import Dict, List

from app.config import get_settings
from app.core.exceptions import NmapExecutionError, ValidationError
from app.core.validators import validate_target_address
from app.models.scan import ScanProfile

logger = logging.getLogger(__name__)
settings = get_settings()

# Fixed, reviewed argument sets. Each list contains ONLY nmap flags — no
# target address and no output-format flags (those are appended
# programmatically in build_nmap_command).
NMAP_PROFILES: Dict[ScanProfile, List[str]] = {
    ScanProfile.QUICK: ["-T4", "-F"],
    ScanProfile.STANDARD: ["-T4", "-sV", "--top-ports", "1000"],
    ScanProfile.FULL_TCP: ["-T4", "-p-", "-sV"],
    ScanProfile.VERSION_DETECTION: ["-T4", "-sV"],
    ScanProfile.OS_DETECTION: ["-T4", "-O"],
}


def build_nmap_command(target_address: str, profile: ScanProfile) -> List[str]:
    """Construct the full, safe Nmap command as a list of arguments.

    Raises ValidationError if the target address or profile is invalid.
    """
    validated_address = validate_target_address(target_address)

    if profile not in NMAP_PROFILES:
        raise ValidationError(f"Unknown or unsupported scan profile: {profile}")

    profile_args = NMAP_PROFILES[profile]

    # XML output is written to stdout ("-oX -") so no output file needs to
    # be created, tracked, or cleaned up on disk.
    command = [
        settings.NMAP_PATH,
        *profile_args,
        "-oX",
        "-",
        validated_address,
    ]
    return command


def run_nmap_scan(target_address: str, profile: ScanProfile) -> str:
    """Execute an Nmap scan and return the raw XML output as a string.

    Raises:
        ValidationError: invalid target address or unknown profile.
        NmapExecutionError: nmap binary missing, non-zero exit, or timeout.
    """
    command = build_nmap_command(target_address, profile)
    logger.info("Executing nmap scan: %s", " ".join(command))

    try:
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            timeout=settings.NMAP_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise NmapExecutionError(
            f"Nmap executable not found at '{settings.NMAP_PATH}'. "
            "Verify Nmap is installed and NMAP_PATH is configured correctly."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise NmapExecutionError(
            "Nmap scan exceeded the configured timeout of "
            f"{settings.NMAP_TIMEOUT_SECONDS} seconds and was terminated."
        ) from exc

    if result.returncode != 0:
        stderr_snippet = (result.stderr or "").strip()[:1000]
        raise NmapExecutionError(
            f"Nmap exited with status {result.returncode}. {stderr_snippet}"
        )

    if not result.stdout or not result.stdout.strip():
        raise NmapExecutionError("Nmap produced no output.")

    return result.stdout


def get_available_profiles() -> List[str]:
    """Return the list of scan profile names available to clients."""
    return [profile.value for profile in NMAP_PROFILES.keys()]