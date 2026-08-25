from __future__ import annotations

from codex_bridge import create_bridge_app
from codex_runtime import CodexRuntimeStatus


class FakeCodexRuntime:
    def __init__(self):
        self.calls: list[dict] = []

    def run_json(self, **kwargs):
        self.calls.append(kwargs)
        return {"answer": "structured host result"}


def test_bridge_requires_token_and_forwards_a_constrained_run():
    runtime = FakeCodexRuntime()
    app = create_bridge_app(
        runtime=runtime,
        token="bridge-secret-0123456789-abcdefghij",
        status_factory=lambda: CodexRuntimeStatus(True, "codex-cli test", "Ready."),
    )
    client = app.test_client()

    assert client.get("/health").status_code == 401

    headers = {"Authorization": "Bearer bridge-secret-0123456789-abcdefghij"}
    health = client.get("/health", headers=headers)
    response = client.post(
        "/v1/structured",
        headers=headers,
        json={
            "prompt": "Research safely.",
            "output_schema": {"type": "object"},
            "enable_search": True,
        },
    )

    assert health.get_json()["available"] is True
    assert response.status_code == 200
    assert response.get_json() == {"result": {"answer": "structured host result"}}
    assert runtime.calls == [
        {
            "prompt": "Research safely.",
            "output_schema": {"type": "object"},
            "enable_search": True,
        }
    ]
