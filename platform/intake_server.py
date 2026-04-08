"""
DNA Intake Server — Branch 3: Economic Autonomy
================================================

Minimal FastAPI server that exposes the intake pipeline as an HTTP API.
Clients submit their filled questionnaire via POST; the server synthesizes
a dna_core.md and returns the result (or queues it for async delivery).

Endpoints:
    GET  /form             — returns blank intake questionnaire (markdown)
    POST /submit           — accepts filled form JSON, runs synthesis+validation
    GET  /report/{id}      — fetch completed report by submission ID
    GET  /health           — status check
    GET  /tree             — returns results/dynamic_tree.md as text/markdown (404 if missing)
    GET  /paper-live-log   — returns last 20 entries from paper_live_log.jsonl as JSON list

Usage:
    ANTHROPIC_API_KEY=sk-... uvicorn platform.intake_server:app --port 8080

    # or direct:
    ANTHROPIC_API_KEY=sk-... python platform/intake_server.py

Deployment notes:
    - ANTHROPIC_API_KEY must be set
    - Reports persist to results/intake_reports/ (gitignored for privacy)
    - For production: add auth token header (INTAKE_API_KEY env var)
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Lazy import so the file is importable without fastapi installed
try:
    from fastapi import FastAPI, Header, HTTPException, Request
    from fastapi.responses import JSONResponse, PlainTextResponse
    import uvicorn
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False

# Inject repo root into sys.path so we can import intake
sys.path.insert(0, str(REPO_ROOT))
from intake import INTAKE_FORM, run_pipeline, synthesize_dna, validate_dna  # noqa: E402

REPORTS_DIR = REPO_ROOT / "results" / "intake_reports"

# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _check_auth(x_api_key: str | None) -> None:
    """If INTAKE_API_KEY is set, validate the header. Skip auth if not set."""
    expected = os.environ.get("INTAKE_API_KEY", "")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ---------------------------------------------------------------------------
# Report persistence
# ---------------------------------------------------------------------------

def _save_report(submission_id: str, intake_md: str, dna_md: str,
                 validation: dict) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "id": submission_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intake": intake_md,
        "dna": dna_md,
        "validation": validation,
    }
    path = REPORTS_DIR / f"{submission_id}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _load_report(submission_id: str) -> dict | None:
    path = REPORTS_DIR / f"{submission_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def build_app() -> "FastAPI":
    app = FastAPI(
        title="DNA Calibration Intake API",
        description="Submit a filled intake questionnaire → receive a calibrated dna_core.md",
        version="1.0.0",
    )

    @app.get("/health")
    def health() -> dict:
        api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
        return {"status": "ok", "api_key_configured": api_key_set}

    @app.get("/tree", response_class=PlainTextResponse)
    def get_tree() -> PlainTextResponse:
        """Return the dynamic tree as plain markdown."""
        tree_path = REPO_ROOT / "results" / "dynamic_tree.md"
        if not tree_path.exists():
            raise HTTPException(status_code=404, detail="dynamic_tree.md not found")
        content = tree_path.read_text(encoding="utf-8")
        return PlainTextResponse(content=content, media_type="text/markdown")

    @app.get("/paper-live-log")
    def get_paper_live_log() -> list:
        """Return the last 20 entries from the paper-live trading log as a JSON list."""
        log_path = REPO_ROOT / "results" / "paper_live_log.jsonl"
        if not log_path.exists():
            return []
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        entries = []
        for raw in lines[-20:]:
            try:
                entries.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        return entries

    @app.get("/form", response_class=PlainTextResponse)
    def get_form(x_api_key: str | None = Header(default=None)) -> str:
        """Return the blank intake questionnaire as plain markdown."""
        _check_auth(x_api_key)
        return INTAKE_FORM

    @app.post("/submit")
    async def submit_intake(
        request: Request,
        x_api_key: str | None = Header(default=None),
        model: str = "claude-haiku-4-5-20251001",
    ) -> dict:
        """
        Submit a filled intake form.

        Body: plain text (markdown) — the filled questionnaire.
        Returns: { id, verdict, score, dna_preview } immediately.

        model param: use haiku for cost-efficient batch, sonnet for precision.
        """
        _check_auth(x_api_key)

        if "ANTHROPIC_API_KEY" not in os.environ:
            raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured")

        intake_text = (await request.body()).decode("utf-8")
        if len(intake_text) < 200:
            raise HTTPException(
                status_code=400,
                detail="Intake form too short — fill all required sections",
            )

        # Write intake to temp file
        submission_id = str(uuid.uuid4())[:8]
        tmp_dir = REPORTS_DIR / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        intake_path = tmp_dir / f"{submission_id}_intake.md"
        dna_path = tmp_dir / f"{submission_id}_dna_core.md"
        intake_path.write_text(intake_text, encoding="utf-8")

        try:
            synthesize_dna(intake_path, dna_path, model)
            dna_text = dna_path.read_text(encoding="utf-8")
            validation = validate_dna(dna_path, model)
        finally:
            intake_path.unlink(missing_ok=True)
            dna_path.unlink(missing_ok=True)

        _save_report(submission_id, intake_text, dna_text, validation)

        return {
            "id": submission_id,
            "verdict": validation["verdict"],
            "score": validation["score"],
            "dna_lines": len(dna_text.splitlines()),
            "dna_preview": dna_text[:500] + ("…" if len(dna_text) > 500 else ""),
        }

    @app.get("/report/{submission_id}")
    def get_report(
        submission_id: str,
        x_api_key: str | None = Header(default=None),
    ) -> dict:
        """Fetch the full DNA report for a prior submission."""
        _check_auth(x_api_key)
        record = _load_report(submission_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Report not found")
        return record

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not _HAS_FASTAPI:
        print("ERROR: fastapi and uvicorn are required.")
        print("Install: pip install fastapi uvicorn")
        sys.exit(1)

    app = build_app()
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting DNA Intake Server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
else:
    if _HAS_FASTAPI:
        app = build_app()
