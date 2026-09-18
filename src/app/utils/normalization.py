"""String and entity normalization utilities."""

from __future__ import annotations

from typing import List


def normalize_person_list(persons: List[str]) -> List[str]:
    """Normalize a list of extracted person names for fair comparison.

    Strips leading and trailing whitespace from each name and removes
    any empty strings. Preserves original order; sorting for order-insensitive
    comparison should be handled by the caller.

    Parameters
    ----------
    persons : list of str
        The raw extracted names or ground truth names.

    Returns
    -------
    list of str
        Cleaned non-empty person name strings.

    Examples
    --------
    >>> normalize_person_list(["  Albert Einstein  ", "", "Niels Bohr "])
    ['Albert Einstein', 'Niels Bohr']
    >>> normalize_person_list([])
    []
    >>> normalize_person_list(["   "])
    []
    """
    normalized: List[str] = []
    for name in persons:
        cleaned = name.strip()
        if cleaned:
            normalized.append(cleaned)
    return normalized

