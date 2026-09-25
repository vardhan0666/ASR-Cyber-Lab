"""
Optional AI-assisted explanation service.

AI is OPTIONAL ASSISTANCE ONLY and is NEVER the source of truth for
security findings. This service:
  - is fully disabled unless AI_ENABLED=true AND an AI_API_KEY/AI_PROVIDER
    are explicitly configured
  - only ever sends ACTUAL project evidence (finding data already computed
    and persisted by the risk engine/config analysis) to the configured
    provider
  - never allows the AI response to be persisted as a Finding, risk score,
    or vulnerability record — it is a read-only, ephemeral explanation
  - always returns the original evidence alongside any AI-generated text
    so the output can be independently verified
  - fails safe: if AI is disabled, misconfigured, or the provider call
    fails for any reason, an explicit "unavailable" result is returned
    instead of raising an error that would break the rest of the API

Uses only the Python standard library for the optional HTTP call, so no
additional production dependency is required for this feature.
"""

import json
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.config import get_settings

settings = get_settings()

_REQUEST_TIMEOUT_SECONDS = 20


@dataclass
class AIExplanationResult:
    available: bool
    summary: Optional[str] = None
    note: str = ""
    evidence_used: Dict[str, Any] = field(default_factory=dict)


def is_ai_enabled() -> bool:
    return bool(settings.AI_ENABLED) and bool(settings.AI_API_KEY) and settings.AI_PROVIDER != "none"


def _build_prompt(finding_evidence: Dict[str, Any]) -> str:
    return (
        "You are assisting a defensive security analyst. You are given "
        "ACTUAL evidence collected by an authorized security scan below as "
        "JSON. Summarize it in plain language for a security report. "
        "Strictly distinguish EVIDENCE (directly observed facts), "
        "INFERENCE (reasonable interpretation of the evidence), and "
        "RECOMMENDATION (suggested next step). Do NOT invent any facts, "
        "CVEs, ports, services, or scores not present in the evidence "
        "below. If information is insufficient to say something, state "
        "that explicitly instead of guessing.\n\n"
        f"EVIDENCE JSON:\n{json.dumps(finding_evidence, default=str)}"
    )


def explain_finding_evidence(finding_evidence: Dict[str, Any]) -> AIExplanationResult:
    """Generate an optional AI-assisted natural-language explanation of a
    finding's evidence. Always returns a well-formed result; never raises
    for AI-availability reasons."""
    if not is_ai_enabled():
        return AIExplanationResult(
            available=False,
            note=(
                "AI assistance is disabled or not configured "
                "(AI_ENABLED=false or no AI_API_KEY/AI_PROVIDER set). "
                "Findings, risk scores, and remediation shown elsewhere in "
                "this platform are produced entirely by the deterministic "
                "risk engine and are unaffected by this setting."
            ),
            evidence_used=finding_evidence,
        )

    prompt = _build_prompt(finding_evidence)

    try:
        summary = _call_openai_compatible(prompt)
    except Exception as exc:  # noqa: BLE001 - any provider failure must fail safe
        return AIExplanationResult(
            available=False,
            note=f"AI provider call failed and no explanation was generated: {exc}",
            evidence_used=finding_evidence,
        )

    return AIExplanationResult(
        available=True,
        summary=summary,
        note=(
            "AI-generated summary. This is optional assistance only — it "
            "is not a source of truth. Verify against the evidence and "
            "risk engine explanation shown alongside it."
        ),
        evidence_used=finding_evidence,
    )


def _call_openai_compatible(prompt: str) -> str:
    """Minimal call to an OpenAI-compatible chat completions endpoint.
    Raises on any failure — callers must handle it and fail safe."""
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 500,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.AI_API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        body = json.loads(response.read().decode("utf-8"))

    choices = body.get("choices", [])
    if not choices:
        raise ValueError("AI provider returned no choices")

    message = choices[0].get("message", {})
    content = message.get("content")
    if not content:
        raise ValueError("AI provider returned an empty response")

    return content