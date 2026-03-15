"""
Tests for the Containment Geometry Validator (containment_validator.py).
"""

from recursive_field_math.containment_validator import MIN_LAYERS, validate

# ---------------------------------------------------------------------------
# Sample specs
# ---------------------------------------------------------------------------

SIMPLE_SPEC = {
    "layers": {
        "core": {"depends_on": []},
        "service": {"depends_on": ["core"]},
        "api": {"depends_on": ["service"]},
    }
}

STAR_SPEC = {
    "layers": {
        "hub": {"depends_on": []},
        "spoke1": {"depends_on": ["hub"]},
        "spoke2": {"depends_on": ["hub"]},
        "spoke3": {"depends_on": ["hub"]},
    }
}

CIRCULAR_SPEC = {
    "layers": {
        "a": {"depends_on": ["b"]},
        "b": {"depends_on": ["a"]},
        "c": {"depends_on": []},
    }
}

WEIGHTED_SPEC = {
    "layers": {
        "foundation": {"depends_on": [], "weight": 3.0},
        "middleware": {"depends_on": ["foundation"], "weight": 2.0},
        "facade": {"depends_on": ["middleware", "foundation"], "weight": 1.0},
    }
}


# ---------------------------------------------------------------------------
# Core success path tests
# ---------------------------------------------------------------------------


def test_simple_spec_ok():
    result = validate(SIMPLE_SPEC)
    assert result["ok"] is True
    assert result["n_layers"] == 3  # noqa: PLR2004
    assert result["n_couplings"] == 2  # noqa: PLR2004  # service→core, api→service
    assert 0.0 <= result["containment_score"] <= 1.0


def test_star_spec_ok():
    result = validate(STAR_SPEC)
    assert result["ok"] is True
    assert result["n_layers"] == 4  # noqa: PLR2004


def test_circular_spec_ok():
    """Circular deps should not crash – validator handles them gracefully."""
    result = validate(CIRCULAR_SPEC)
    assert result["ok"] is True


def test_weighted_spec_ok():
    result = validate(WEIGHTED_SPEC)
    assert result["ok"] is True
    assert result["n_couplings"] >= 2  # noqa: PLR2004


def test_containment_score_range():
    for spec in (SIMPLE_SPEC, STAR_SPEC, CIRCULAR_SPEC, WEIGHTED_SPEC):
        result = validate(spec)
        assert 0.0 <= result["containment_score"] <= 1.0


def test_weak_layer_map_all_layers_present():
    result = validate(SIMPLE_SPEC)
    assert set(result["weak_layer_map"].keys()) == {"core", "service", "api"}


def test_weak_layer_map_values_in_range():
    result = validate(WEIGHTED_SPEC)
    for score in result["weak_layer_map"].values():
        assert 0.0 <= score <= 1.0


def test_escape_path_candidates_is_list():
    result = validate(SIMPLE_SPEC)
    assert isinstance(result["escape_path_candidates"], list)


def test_escape_path_tuples_structure():
    result = validate(WEIGHTED_SPEC)
    for item in result["escape_path_candidates"]:
        src, dst, severity = item
        assert isinstance(src, str)
        assert isinstance(dst, str)
        assert 0.0 <= severity <= 1.0


def test_top_k_escapes_respected():
    result = validate(STAR_SPEC, top_k_escapes=1)
    assert len(result["escape_path_candidates"]) <= 1


# ---------------------------------------------------------------------------
# Fail-closed tests
# ---------------------------------------------------------------------------


def test_missing_layers_key_returns_not_ok():
    result = validate({})
    assert result["ok"] is False
    assert "layers" in result["reason"].lower()


def test_single_layer_returns_not_ok():
    result = validate({"layers": {"only": {"depends_on": []}}})
    assert result["ok"] is False
    assert str(MIN_LAYERS) in result["reason"]


def test_empty_layers_returns_not_ok():
    result = validate({"layers": {}})
    assert result["ok"] is False


# ---------------------------------------------------------------------------
# Determinism tests
# ---------------------------------------------------------------------------


def test_validate_is_deterministic():
    r1 = validate(WEIGHTED_SPEC)
    r2 = validate(WEIGHTED_SPEC)
    assert r1 == r2


# ---------------------------------------------------------------------------
# Dangling dependency handling
# ---------------------------------------------------------------------------


def test_dangling_dep_ignored():
    """A dependency on a non-existent layer should be silently ignored."""
    spec = {
        "layers": {
            "a": {"depends_on": ["nonexistent"]},
            "b": {"depends_on": ["a"]},
            "c": {"depends_on": []},
        }
    }
    result = validate(spec)
    assert result["ok"] is True


# ---------------------------------------------------------------------------
# No-coupling (isolated layers) test
# ---------------------------------------------------------------------------


def test_fully_isolated_high_containment():
    """Layers with no dependencies should yield a high containment score."""
    spec = {
        "layers": {
            "island1": {"depends_on": []},
            "island2": {"depends_on": []},
            "island3": {"depends_on": []},
        }
    }
    result = validate(spec)
    assert result["ok"] is True
    # No couplings at all
    assert result["n_couplings"] == 0
    # Containment score should be high (close to 1)
    assert result["containment_score"] > 0.5  # noqa: PLR2004
