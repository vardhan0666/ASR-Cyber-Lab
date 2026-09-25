"""
Application logging configuration.

Two logical loggers are used:
  - root/application logger: general operational logs.
  - "audit" logger: security-relevant events (auth, scans, target changes).

The audit logger is intentionally kept separate so audit records can later
be routed independently (e.g., to a file or external sink) without changing
call sites.
"""

import logging
import sys

from app.config import get_settings

settings = get_settings()

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging() -> None:
    """Configure root logging handlers. Safe to call once at app startup."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers on reload (e.g., uvicorn --reload).
    if root_logger.handlers:
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    root_logger.addHandler(handler)

    # Reduce noise from uvicorn's access log; audit logger covers security events.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = True


def get_audit_logger() -> logging.Logger:
    """Return the dedicated audit logger instance."""
    return logging.getLogger("audit")