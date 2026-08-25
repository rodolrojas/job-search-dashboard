from __future__ import annotations

from pathlib import Path

from cover_letters import CoverLetterDraft, generate_cover_letter


class FakeCodexRuntime:
    def __init__(self, content: str = "Dear Example Hiring Team,\n\nA Codex-written draft.\n"):
        self.content = content
        self.prompt = ""
        self.enable_search: bool | None = None

    def run_structured(self, *, prompt: str, result_type: type[CoverLetterDraft], enable_search: bool):
        self.prompt = prompt
        self.enable_search = enable_search
        return result_type(content=self.content)


class FailingCodexRuntime:
    def run_structured(self, **_kwargs):
        raise RuntimeError("Codex is unavailable")


def _job() -> dict:
    return {
        "company": "Example Co",
        "role": "Senior Python Engineer",
        "strategic_note": "The backend ownership matches the candidate's experience.",
    }


def _profile() -> dict:
    return {
        "basics": {"name": "Rodolfo Rojas"},
        "summary": ["I build production full-stack applications."],
        "skills": ["Python", "React"],
        "variants": {"backend": {"headline": "Backend Engineer"}},
    }


def test_cover_letter_uses_codex_structured_output(tmp_path: Path):
    runtime = FakeCodexRuntime()

    result = generate_cover_letter(
        job=_job(),
        profile=_profile(),
        variant_key="backend",
        output_root=tmp_path,
        runtime=runtime,
    )

    assert result["mode"] == "codex"
    assert result["warning"] is None
    assert result["content"] == runtime.content
    assert runtime.enable_search is False
    assert '"resume_variant": "backend"' in runtime.prompt
    assert (tmp_path / result["filename"]).read_text(encoding="utf-8") == runtime.content


def test_cover_letter_falls_back_when_codex_fails(tmp_path: Path):
    result = generate_cover_letter(
        job=_job(),
        profile=_profile(),
        variant_key="backend",
        output_root=tmp_path,
        runtime=FailingCodexRuntime(),
    )

    assert result["mode"] == "local"
    assert "Codex generation was unavailable" in result["warning"]
    assert "Example Co Hiring Team" in result["content"]
    assert (tmp_path / result["filename"]).is_file()
