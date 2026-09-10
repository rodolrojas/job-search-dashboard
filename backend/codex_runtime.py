from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel


StructuredResult = TypeVar("StructuredResult", bound=BaseModel)
ProcessRunner = Callable[..., subprocess.CompletedProcess[str]]
UrlOpener = Callable[..., Any]
BRIDGE_TOKEN_PLACEHOLDER = "replace-with-a-long-random-secret"


@dataclass(frozen=True)
class CodexRuntimeStatus:
    available: bool
    version: str | None
    message: str


def resolve_codex_command(command: str | None = None) -> str | None:
    """Resolve an explicit CLI path first, then the host's PATH."""

    requested = (command or os.getenv("CODEX_CLI_PATH") or "codex").strip()
    if not requested:
        return None
    requested_path = Path(requested).expanduser()
    if requested_path.is_file():
        return str(requested_path.resolve())
    return shutil.which(requested)


def codex_cli_status(
    command: str | None = None,
    *,
    runner: ProcessRunner = subprocess.run,
) -> CodexRuntimeStatus:
    """Check that the host Codex CLI exists and can be launched."""

    resolved = resolve_codex_command(command)
    if not resolved:
        return CodexRuntimeStatus(
            available=False,
            version=None,
            message="Codex CLI was not found. Install it on the host and sign in with codex login.",
        )
    try:
        completed = runner(
            [resolved, "--version"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return CodexRuntimeStatus(
            available=False,
            version=None,
            message=f"Codex CLI could not be launched ({type(error).__name__}).",
        )
    if completed.returncode != 0:
        return CodexRuntimeStatus(
            available=False,
            version=None,
            message="Codex CLI is installed but did not start successfully.",
        )
    version = (completed.stdout or completed.stderr).strip() or "Codex CLI"
    try:
        login_status = runner(
            [resolved, "login", "status"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return CodexRuntimeStatus(
            available=False,
            version=version,
            message=f"Codex authentication status could not be checked ({type(error).__name__}).",
        )
    if login_status.returncode != 0:
        return CodexRuntimeStatus(
            available=False,
            version=version,
            message="Codex CLI is installed but is not signed in. Run codex login on the host.",
        )
    return CodexRuntimeStatus(
        available=True,
        version=version,
        message="Using the signed-in Codex CLI from this host machine.",
    )


def codex_runtime_status() -> CodexRuntimeStatus:
    """Probe the configured direct-CLI or authenticated bridge transport."""

    bridge_url = (os.getenv("CODEX_BRIDGE_URL") or "").strip()
    if bridge_url:
        return codex_bridge_status(bridge_url=bridge_url)
    return codex_cli_status()


def codex_provider_name() -> str:
    return "Host Codex bridge" if (os.getenv("CODEX_BRIDGE_URL") or "").strip() else "Host Codex CLI"


def create_codex_runtime(*, workspace: Path) -> CodexCliRunner | CodexBridgeRuntime:
    bridge_url = (os.getenv("CODEX_BRIDGE_URL") or "").strip()
    if bridge_url:
        return CodexBridgeRuntime(bridge_url=bridge_url)
    return CodexCliRunner(workspace=workspace)


class CodexCliRunner:
    """Safe structured-output adapter around the host's `codex exec` command."""

    provider = "Host Codex CLI"

    def __init__(
        self,
        *,
        workspace: Path,
        command: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
        runner: ProcessRunner = subprocess.run,
    ):
        resolved = resolve_codex_command(command)
        if not resolved:
            raise RuntimeError("Codex CLI was not found on the host PATH. Set CODEX_CLI_PATH if needed.")
        self.command = resolved
        self.workspace = workspace.resolve()
        self.model_override = (model or os.getenv("CODEX_MODEL") or "").strip() or None
        self.model = self.model_override or "host default"
        self.timeout_seconds = timeout_seconds or int(os.getenv("CODEX_TIMEOUT_SECONDS", "600"))
        self.runner = runner

    def run_structured(
        self,
        *,
        prompt: str,
        result_type: type[StructuredResult],
        enable_search: bool,
    ) -> StructuredResult:
        """Run one non-interactive, read-only Codex turn and validate its final JSON."""

        result = self.run_json(
            prompt=prompt,
            output_schema=result_type.model_json_schema(),
            enable_search=enable_search,
        )
        try:
            return result_type.model_validate(result)
        except ValueError as error:
            raise RuntimeError("Codex CLI returned a response that failed schema validation.") from error

    def run_json(
        self,
        *,
        prompt: str,
        output_schema: dict[str, Any],
        enable_search: bool,
    ) -> dict[str, Any]:
        """Run Codex against a supplied schema and return the decoded JSON object."""

        if not self.workspace.is_dir():
            raise RuntimeError(f"Codex workspace does not exist: {self.workspace}")

        with tempfile.TemporaryDirectory(prefix="role-radar-codex-") as temp_dir:
            temp_root = Path(temp_dir)
            schema_path = temp_root / "response.schema.json"
            result_path = temp_root / "response.json"
            schema_path.write_text(
                json.dumps(output_schema, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            command: list[str] = [
                self.command,
                "exec",
                "--cd",
                str(self.workspace),
                "--sandbox",
                "read-only",
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(result_path),
            ]
            if self.model_override:
                command.extend(["--model", self.model_override])
            command.append("-")

            try:
                completed = self.runner(
                    command,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(
                    f"Codex CLI exceeded the {self.timeout_seconds}-second run limit."
                ) from error
            except OSError as error:
                raise RuntimeError(f"Codex CLI could not be launched ({type(error).__name__}).") from error

            if completed.returncode != 0:
                details = _compact_process_error(completed.stderr or completed.stdout)
                raise RuntimeError(f"Codex CLI exited with code {completed.returncode}: {details}")
            if not result_path.is_file():
                raise RuntimeError("Codex CLI completed without writing its structured final response.")
            try:
                payload = json.loads(result_path.read_text(encoding="utf-8"))
            except (ValueError, json.JSONDecodeError) as error:
                raise RuntimeError("Codex CLI returned invalid JSON.") from error
            if not isinstance(payload, dict):
                raise RuntimeError("Codex CLI returned JSON that was not an object.")
            return payload


class CodexBridgeRuntime:
    """Structured Codex client for a Docker backend talking to its host."""

    provider = "Host Codex bridge"

    def __init__(
        self,
        *,
        bridge_url: str,
        token: str | None = None,
        timeout_seconds: int | None = None,
        opener: UrlOpener = urlopen,
    ):
        self.bridge_url = bridge_url.rstrip("/")
        self.token = (token or os.getenv("CODEX_BRIDGE_TOKEN") or "").strip()
        if not _bridge_token_is_valid(self.token):
            raise RuntimeError("CODEX_BRIDGE_TOKEN must be a non-placeholder secret of at least 32 characters.")
        self.timeout_seconds = timeout_seconds or int(os.getenv("CODEX_TIMEOUT_SECONDS", "600"))
        self.opener = opener
        self.model = "host bridge default"

    def run_structured(
        self,
        *,
        prompt: str,
        result_type: type[StructuredResult],
        enable_search: bool,
    ) -> StructuredResult:
        request = Request(
            f"{self.bridge_url}/v1/structured",
            data=json.dumps(
                {
                    "prompt": prompt,
                    "output_schema": result_type.model_json_schema(),
                    "enable_search": enable_search,
                },
                ensure_ascii=False,
            ).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with self.opener(request, timeout=self.timeout_seconds + 15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            details = _http_error_details(error)
            raise RuntimeError(f"Codex host bridge rejected the run (HTTP {error.code}): {details}") from error
        except (URLError, TimeoutError, OSError, ValueError) as error:
            raise RuntimeError(f"Codex host bridge was unavailable ({type(error).__name__}).") from error
        try:
            return result_type.model_validate(payload["result"])
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError("Codex host bridge returned an invalid structured response.") from error


def codex_bridge_status(
    *,
    bridge_url: str,
    token: str | None = None,
    opener: UrlOpener = urlopen,
) -> CodexRuntimeStatus:
    resolved_token = (token or os.getenv("CODEX_BRIDGE_TOKEN") or "").strip()
    if not _bridge_token_is_valid(resolved_token):
        return CodexRuntimeStatus(False, None, "Set a random CODEX_BRIDGE_TOKEN of at least 32 characters.")
    request = Request(
        f"{bridge_url.rstrip('/')}/health",
        headers={"Authorization": f"Bearer {resolved_token}"},
        method="GET",
    )
    try:
        with opener(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        return CodexRuntimeStatus(False, None, f"Codex host bridge rejected the health check (HTTP {error.code}).")
    except (URLError, TimeoutError, OSError, ValueError) as error:
        return CodexRuntimeStatus(False, None, f"Codex host bridge is unavailable ({type(error).__name__}).")
    return CodexRuntimeStatus(
        available=bool(payload.get("available")),
        version=payload.get("version"),
        message=str(payload.get("message") or "Codex host bridge is unavailable."),
    )


def _compact_process_error(value: Any) -> str:
    text = str(value or "No error details were returned.").strip()
    if len(text) > 1_200:
        text = text[-1_200:]
    return " ".join(text.split())


def _http_error_details(error: HTTPError) -> str:
    try:
        payload = json.loads(error.read().decode("utf-8"))
        return _compact_process_error(payload.get("error"))
    except (ValueError, OSError):
        return error.reason or "Request failed."


def _bridge_token_is_valid(token: str) -> bool:
    return len(token) >= 32 and token != BRIDGE_TOKEN_PLACEHOLDER
