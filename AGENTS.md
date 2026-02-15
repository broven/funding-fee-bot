# AGENTS

## Python dependency policy

- Use `uv` for dependency and environment management.
- Do not use `pip install`, `requirements.txt`, `pipenv`, or `poetry` in this repo.
- Keep dependencies in `pyproject.toml` and lock them in `uv.lock`.
- After any dependency change, run:

```bash
uv lock
uv sync --extra dev
```

## Test commands

- Unit tests:

```bash
uv run pytest tests/unit -v
```

- Optional live test:

```bash
RUN_LIVE_TESTS=1 uv run pytest tests/integration/test_binance_live.py -v
```
