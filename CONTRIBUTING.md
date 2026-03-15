# Contributing

## Development flow
1. Create a branch from `main`
2. Make focused changes
3. Run local quality checks
4. Open PR with completed template

## Local checks (Python)
```bash
ruff check .
black --check .
flake8 .
mypy . --ignore-missing-imports
pytest -q
```

## Commit format
Use Conventional Commits:
- `feat:`
- `fix:`
- `docs:`
- `ci:`
- `refactor:`
- `test:`
- `chore:`
- `security:`
