"""Pydantic request/response schemas for the API layer.

Route modules import directly from the individual schema files
(e.g. `from app.schemas.target import TargetCreate`) rather than through
this package's namespace, to keep import graphs explicit and avoid
accidental circular imports.
"""