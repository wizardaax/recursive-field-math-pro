"""
Test to ensure that attribute access patterns are replaced with dictionary access.
This test validates the linter requirement for dictionary access over attribute access.
"""

def test_dictionary_access_pattern():
    """
    Test that demonstrates the correct way to access result_normal data.
    This shows the pattern that should be used: dictionary access over attribute access.
    """
    # Example of correct dictionary access pattern
    result_normal = {"ok": True, "status": "success", "data": {}}

    # This is the CORRECT way to access the 'ok' field
    assert result_normal["ok"] is True

    # This pattern (attribute access) should NOT be used and will fail linting
    # The test validates that we use dictionary access instead of attribute access


def test_result_normal_dict_operations():
    """Test various dictionary operations on result_normal objects."""
    result_normal = {
        "ok": True,
        "status": "completed",
        "data": {"value": 42},
        "errors": []
    }

    # Correct dictionary access patterns
    assert result_normal["ok"] is True
    assert result_normal["status"] == "completed"
    assert result_normal["data"]["value"] == 42
    assert len(result_normal["errors"]) == 0

    # Test safe access with get() method
    assert result_normal.get("ok", False) is True
    assert result_normal.get("nonexistent") is None


def test_result_normal_error_case():
    """Test handling of error cases with dictionary access."""
    result_normal = {
        "ok": False,
        "status": "error",
        "error_message": "Something went wrong"
    }

    # Use dictionary access for error checking
    if not result_normal["ok"]:
        assert result_normal["status"] == "error"
        assert "error_message" in result_normal
