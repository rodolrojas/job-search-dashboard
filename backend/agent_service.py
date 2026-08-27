from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from contextlib import nullcontext
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, ContextManager

from job_search_agent import JobSearchAgent


class AgentRunRegistry:
    """Small in-process run registry suitable for one Docker API process."""

    def __init__(
        self,
        agent_factory: Callable[[], JobSearchAgent],
        on_complete: Callable[[dict[str, Any]], None] | None = None,
        on_change: Callable[[dict[str, Any]], None] | None = None,
        run_context_factory: Callable[[], ContextManager[Any]] | None = None,
        initial_runs: list[dict[str, Any]] | None = None,
    ):
        self.agent_factory = agent_factory
        self.on_complete = on_complete
        self.on_change = on_change
        self.run_context_factory = run_context_factory
        self._lock = threading.Lock()
        self._runs = {run["id"]: deepcopy(run) for run in (initial_runs or [])}
        self._latest_id = max(
            self._runs,
            key=lambda run_id: self._runs[run_id].get("created_at", ""),
            default=None,
        )

    def start(self) -> dict[str, Any]:
        with self._lock:
            if self._latest_id and self._runs[self._latest_id]["status"] in {"queued", "running"}:
                raise RuntimeError("A job-search agent run is already active.")
            run_id = uuid.uuid4().hex
            now = datetime.now(UTC).isoformat()
            self._runs[run_id] = {
                "id": run_id,
                "status": "queued",
                "phase": "queued",
                "message": "Agent run queued.",
                "created_at": now,
                "updated_at": now,
                "events": [],
                "result": None,
                "error": None,
            }
            self._latest_id = run_id
            snapshot = deepcopy(self._runs[run_id])
        self._notify(snapshot)
        threading.Thread(target=self._execute, args=(run_id,), daemon=True, name=f"job-agent-{run_id[:8]}").start()
        return snapshot

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            run = self._runs.get(run_id)
            return deepcopy(run) if run else None

    def latest(self) -> dict[str, Any] | None:
        with self._lock:
            run = self._runs.get(self._latest_id) if self._latest_id else None
            return deepcopy(run) if run else None

    def _emit(self, run_id: str, phase: str, message: str, details: dict[str, Any] | None) -> None:
        with self._lock:
            run = self._runs[run_id]
            now = datetime.now(UTC).isoformat()
            run.update(status="running", phase=phase, message=message, updated_at=now)
            run["events"].append({"phase": phase, "message": message, "details": details, "created_at": now})
            snapshot = deepcopy(run)
        self._notify(snapshot)

    def _execute(self, run_id: str) -> None:
        try:
            context = self.run_context_factory() if self.run_context_factory else nullcontext()
            with context:
                agent = self.agent_factory()
                result = agent.run(lambda phase, message, details=None: self._emit(run_id, phase, message, details))
                if self.on_complete:
                    self.on_complete(result)
            with self._lock:
                now = datetime.now(UTC).isoformat()
                self._runs[run_id].update(
                    status="completed",
                    phase="complete",
                    message=f"Agent completed with {result['result_count']} recommendations.",
                    result=result,
                    updated_at=now,
                )
                snapshot = deepcopy(self._runs[run_id])
            self._notify(snapshot)
        except Exception as error:  # Run state must survive failures for UI inspection.
            with self._lock:
                now = datetime.now(UTC).isoformat()
                self._runs[run_id].update(
                    status="failed",
                    phase="failed",
                    message="Agent run failed.",
                    error=f"{type(error).__name__}: {error}",
                    updated_at=now,
                )
                snapshot = deepcopy(self._runs[run_id])
            self._notify(snapshot)

    def _notify(self, snapshot: dict[str, Any]) -> None:
        if self.on_change:
            self.on_change(snapshot)
