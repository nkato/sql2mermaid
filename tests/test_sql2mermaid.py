from pathlib import Path

import pytest

import sql2mermaid

parent = Path(__file__).parent


@pytest.mark.parametrize(
    ("test_case"),
    [
        ("simple_case"),
        ("normal_case"),
        ("complex_case"),
        ("case_with_extract"),
    ],
)
def test_convert(test_case: Path) -> None:
    query = Path(parent / test_case / "query.sql").read_text()
    expected = Path(parent / test_case / "expected.txt").read_text()
    got = sql2mermaid.convert(query)
    assert got == expected


@pytest.mark.parametrize(
    ("test_case"),
    [
        ("simple_case"),
        ("normal_case"),
        ("complex_case"),
    ],
)
def test_convert_with_upper(test_case: Path) -> None:
    query = Path(parent / test_case / "query.sql").read_text()
    expected = Path(parent / test_case / "expected_with_upper.txt").read_text()
    got = sql2mermaid.convert(query, root_name="changed_root_name", display_join="upper")
    assert got == expected


@pytest.mark.parametrize(
    ("test_case"),
    [
        ("simple_case"),
        ("normal_case"),
        ("complex_case"),
    ],
)
def test_convert_with_lower(test_case: Path) -> None:
    query = Path(parent / test_case / "query.sql").read_text()
    expected = Path(parent / test_case / "expected_with_lower.txt").read_text()
    got = sql2mermaid.convert(query, root_name="changed_root_name", display_join="lower")
    assert got == expected
