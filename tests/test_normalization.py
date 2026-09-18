"""Unit tests for entity list normalization."""

from src.app.utils.normalization import normalize_person_list


def test_normalize_empty_list() -> None:
    """Empty list returns empty list."""
    assert normalize_person_list([]) == []


def test_normalize_whitespace_and_empty_strings() -> None:
    """Whitespace should be trimmed and empty strings removed."""
    raw = ["  Einstein  ", "", "   ", "von Neumann "]
    expected = ["Einstein", "von Neumann"]
    assert normalize_person_list(raw) == expected


def test_normalize_order_preservation() -> None:
    """Original ordering of entities is preserved."""
    raw = ["Person B", "Person A"]
    assert normalize_person_list(raw) == ["Person B", "Person A"]

