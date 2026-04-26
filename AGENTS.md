# AGENTS.md

This repository is a small Python library (`pygamejr` + `codomir`) plus a folder of demo scripts. There is no server and no auth. A `pytest` suite lives under `tests/`.

## Running tests

```bash
source .venv/bin/activate
pip install -e .[test]   # installs pytest if not already available
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy pytest
```

The `tests/conftest.py` sets the SDL dummy drivers automatically, but
exporting them in the parent shell as well keeps the codomir subprocess
tests fast and reliable on a headless VM.

## Skills

- [`.cursor/skills/cloud-agent-starter.md`](.cursor/skills/cloud-agent-starter.md) — **read first.** Practical setup, headless-run instructions, env vars, and per-area testing workflows for Cloud agents. Update this file whenever you discover new testing tricks or runbook knowledge.

## Cursor Cloud specific instructions

- The Cloud VM has no display or audio. Always export `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy` before importing `pygamejr` or `codomir`.
- A `.venv/` is already provisioned with the package installed editable (`pip install -e .`). Activate it with `source .venv/bin/activate`.
- See the starter skill above for end-to-end testing snippets per codebase area.
