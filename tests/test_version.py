"""Test the version of the package."""
import heisskleber


def test_heisskleber_version() -> None:
    """Test that the glue version is correct."""
    assert heisskleber.__version__ == "0.3.1"
