# Codex bridge 502 from unsupported `--search` flag

## Symptom

Starting an agent run through the Dockerized backend can fail with:

```text
RuntimeError: Codex host bridge rejected the run (HTTP 502): Codex CLI exited with code 2: error: unexpected argument '--search' found
tip: to pass '--search' as a value, use '-- --search'
Usage: codex exec [OPTIONS] [PROMPT]
       codex exec [OPTIONS] <COMMAND> [ARGS]
```

`GET /api/agent` can still report `"configured": true` because the bridge health
check only verifies that the host bridge is reachable and that the host Codex CLI
is installed and signed in. The failure happens later, when the bridge starts an
actual structured run.

## Root cause

The backend sends agent work to `backend/codex_bridge.py`, which runs the host
Codex CLI through `CodexCliRunner` in `backend/codex_runtime.py`.

Older application code appended `--search` whenever an agent workflow requested
web search:

```text
codex exec ... --output-schema response.schema.json --output-last-message response.json --search -
```

The installed Codex CLI no longer exposes a `--search` option for `codex exec`.
The current help output lists options such as `--cd`, `--sandbox`,
`--output-schema`, and `--output-last-message`, but not `--search`. Because
argument parsing fails before the model starts, the CLI exits with code 2. The
host bridge wraps that process failure as HTTP 502, and the Docker backend shows
it as `Codex host bridge rejected the run`.

## Fix

Do not pass `--search` to `codex exec`.

The application should keep the `enable_search` field in the bridge request
payload for internal API compatibility, but the local CLI runner must only emit
flags supported by the installed `codex exec` command.

The fixed command shape is:

```text
codex exec --cd <workspace> --sandbox read-only --output-schema <schema> --output-last-message <result> -
```

When a model override is configured, append:

```text
--model <model>
```

## Verification

1. Confirm the local CLI does not support `--search`:

   ```bash
   codex exec --help
   ```

2. Run the backend runtime tests:

   ```bash
   cd backend
   .venv/bin/python -m pytest tests/test_codex_runtime.py -q
   ```

3. Restart the host bridge so it imports the patched runtime:

   ```bash
   cd backend
   .venv/bin/python codex_bridge.py
   ```

4. From the backend container, verify the bridge is reachable:

   ```bash
   docker exec -i job-dashboard-backend-1 python - <<'PY'
   import os
   from urllib.request import Request, urlopen

   url = os.environ["CODEX_BRIDGE_URL"].rstrip("/")
   token = os.environ["CODEX_BRIDGE_TOKEN"]
   request = Request(f"{url}/health", headers={"Authorization": f"Bearer {token}"})
   with urlopen(request, timeout=15) as response:
       print(response.status)
       print(response.read().decode())
   PY
   ```

5. Start an agent run again. If it still fails with HTTP 502, inspect the bridge
   process output first because that is where host-side `codex exec` failures are
   surfaced.
