"""Test the version of the package."""
import heisskleber


def test_glue_version() -> None:
    """Test that the glue version is correct."""
    assert heisskleber.__version__ == "0.1.0"
