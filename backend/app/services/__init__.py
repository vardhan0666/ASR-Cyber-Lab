"""
Service layer: business logic that sits between API routes and the
database/subprocess/filesystem. Route modules should be thin — all
non-trivial logic (scanning, parsing, risk scoring, enrichment, reporting)
lives here so it can be tested independently of the HTTP layer.
"""