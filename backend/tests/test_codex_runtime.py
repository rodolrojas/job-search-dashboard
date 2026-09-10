from __future__ import annotations

import json
import subprocess
from pathlib import Path

from pydantic import BaseModel

from codex_runtime import CodexBridgeRuntime, CodexCliRunner, CodexRuntimeStatus, codex_cli_status


class ExampleResult(BaseModel):
    answer: str


def test_codex_runner_uses_stdin_read_only_mode_structured_output_and_supported_flags(tmp_path: Path):
    captured: dict[str, object] = {}
    fake_codex = tmp_path / "codex-test-bin"
    fake_codex.write_text("test executable placeholder", encoding="utf-8")

    def fake_process(command, **kwargs):
        captured["command"] = command
        captured["prompt"] = kwargs["input"]
        output_path = Path(command[command.index("--output-last-message") + 1])
        schema_path = Path(command[command.index("--output-schema") + 1])
        captured["schema"] = json.loads(schema_path.read_text(encoding="utf-8"))
        output_path.write_text('{"answer":"structured"}', encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    runtime = CodexCliRunner(
        workspace=tmp_path,
        command=str(fake_codex),
        model="test-model",
        timeout_seconds=30,
        runner=fake_process,
    )
    result = runtime.run_structured(
        prompt="Research one role.",
        result_type=ExampleResult,
        enable_search=True,
    )

    command = captured["command"]
    assert result.answer == "structured"
    assert captured["prompt"] == "Research one role."
    assert captured["schema"]["title"] == "ExampleResult"
    assert command[-1] == "-"
    assert "--search" not in command
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert command[command.index("--ask-for-approval") + 1] == "never"
    assert command[command.index("--model") + 1] == "test-model"


def test_codex_runtime_status_reports_the_host_version(monkeypatch):
    monkeypatch.setattr("codex_runtime.resolve_codex_command", lambda _command=None: "codex")
    calls: list[list[str]] = []

    def fake_process(command, **_kwargs):
        calls.append(command)
        output = "codex-cli 1.2.3\n" if command[-1] == "--version" else "Logged in\n"
        return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")

    status = codex_cli_status(runner=fake_process)

    assert status == CodexRuntimeStatus(
        available=True,
        version="codex-cli 1.2.3",
        message="Using the signed-in Codex CLI from this host machine.",
    )
    assert calls == [["codex", "--version"], ["codex", "login", "status"]]


def test_codex_bridge_runtime_sends_only_prompt_schema_and_search_flag():
    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b'{"result":{"answer":"from host"}}'

    def fake_open(request, **kwargs):
        captured["url"] = request.full_url
        captured["authorization"] = request.get_header("Authorization")
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = kwargs["timeout"]
        return FakeResponse()

    runtime = CodexBridgeRuntime(
        bridge_url="http://host.docker.internal:8765",
        token="test-secret-0123456789-abcdefghijkl",
        timeout_seconds=30,
        opener=fake_open,
    )
    result = runtime.run_structured(
        prompt="Research safely.",
        result_type=ExampleResult,
        enable_search=True,
    )

    assert result.answer == "from host"
    assert captured["url"] == "http://host.docker.internal:8765/v1/structured"
    assert captured["authorization"] == "Bearer test-secret-0123456789-abcdefghijkl"
    assert captured["payload"]["prompt"] == "Research safely."
    assert captured["payload"]["enable_search"] is True
    assert captured["payload"]["output_schema"]["title"] == "ExampleResult"
    assert captured["timeout"] == 45
