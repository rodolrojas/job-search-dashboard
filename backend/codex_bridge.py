from __future__ import annotations

import hmac
import os
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from codex_runtime import (
    BRIDGE_TOKEN_PLACEHOLDER,
    CodexCliRunner,
    CodexRuntimeStatus,
    codex_cli_status,
)


HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")
_RUN_LOCK = threading.Lock()


def create_bridge_app(
    *,
    runtime: CodexCliRunner | Any | None = None,
    token: str | None = None,
    status_factory: Callable[[], CodexRuntimeStatus] = codex_cli_status,
) -> Flask:
    """Expose one authenticated, schema-constrained Codex operation to Docker."""

    bridge_token = (token or os.getenv("CODEX_BRIDGE_TOKEN") or "").strip()
    if len(bridge_token) < 32 or bridge_token == BRIDGE_TOKEN_PLACEHOLDER:
        raise RuntimeError("Set CODEX_BRIDGE_TOKEN to a non-placeholder secret of at least 32 characters.")
    codex = runtime or CodexCliRunner(
        workspace=Path(os.getenv("CODEX_WORKSPACE") or HERE.parent),
    )
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

    def authorized() -> bool:
        provided = request.headers.get("Authorization", "")
        expected = f"Bearer {bridge_token}"
        return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))

    @app.before_request
    def require_bridge_token():
        if not authorized():
            return jsonify({"error": "Unauthorized Codex bridge request."}), 401
        return None

    @app.get("/health")
    def health():
        status = status_factory()
        return jsonify(
            {
                "available": status.available,
                "version": status.version,
                "message": status.message,
            }
        )

    @app.post("/v1/structured")
    def structured_run():
        payload = request.get_json(silent=True) or {}
        prompt = payload.get("prompt")
        output_schema = payload.get("output_schema")
        enable_search = payload.get("enable_search")
        if not isinstance(prompt, str) or not prompt.strip():
            return jsonify({"error": "prompt must be a non-empty string."}), 400
        if len(prompt) > 1_500_000:
            return jsonify({"error": "prompt exceeds the bridge size limit."}), 413
        if not isinstance(output_schema, dict):
            return jsonify({"error": "output_schema must be a JSON object."}), 400
        if not isinstance(enable_search, bool):
            return jsonify({"error": "enable_search must be a boolean."}), 400
        try:
            with _RUN_LOCK:
                result = codex.run_json(
                    prompt=prompt,
                    output_schema=output_schema,
                    enable_search=enable_search,
                )
        except RuntimeError as error:
            return jsonify({"error": str(error)}), 502
        return jsonify({"result": result})

    return app


if __name__ == "__main__":
    bridge_app = create_bridge_app()
    bridge_app.run(
        host=os.getenv("CODEX_BRIDGE_HOST", "127.0.0.1"),
        port=int(os.getenv("CODEX_BRIDGE_PORT", "8765")),
        debug=False,
        threaded=True,
        use_reloader=False,
    )
