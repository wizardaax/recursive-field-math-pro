# Code Style Guidelines: Dictionary Access

## Prohibition of Attribute Access on Result Objects

This codebase enforces dictionary access over attribute access for result objects to ensure consistent and safe data handling.

### ❌ Prohibited Pattern
```python
# DON'T use attribute access
if result_normal.ok:
    # handle success
```

### ✅ Correct Pattern
```python
# DO use dictionary access
if result_normal["ok"]:
    # handle success
```

## Rationale

1. **Type Safety**: Dictionary access makes it clear that we're working with dictionary-like objects
2. **Linter Compliance**: Our linter configuration enforces this pattern
3. **Consistency**: All result object access should follow the same pattern
4. **Error Prevention**: Dictionary access prevents subtle bugs related to attribute vs key access

## Implementation

### CI/CD Enforcement
- The CI pipeline includes a check that fails if the prohibited pattern is found
- Run locally with: `python scripts/validate_patterns.py`

### Linter Configuration
- Ruff is configured with additional rules to catch related issues
- Configuration in `pyproject.toml` under `[tool.ruff.lint]`

### Testing
- Tests in `tests/test_result_normal_pattern.py` demonstrate correct usage
- All tests must use dictionary access patterns

## Usage Examples

```python
# Checking success status
if result_normal["ok"]:
    data = result_normal["data"]
    
# Safe access with defaults
status = result_normal.get("status", "unknown")

# Error handling
if not result_normal["ok"]:
    error_msg = result_normal.get("error_message", "Unknown error")
```