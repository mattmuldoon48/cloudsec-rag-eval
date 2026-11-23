import pytest
from pydantic import ValidationError

from cloudsec_rag.chunk import chunk_text
from cloudsec_rag.schemas import Chunk


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param(
            "ABCDEFGHIJKL",
            ["ABCDE", "DEFGH", "GHIJK", "JKL"],
            id="preserves-partial-final-window",
        ),
        pytest.param(
            "ABCDEFGHIJK",
            ["ABCDE", "DEFGH", "GHIJK"],
            id="stops-at-exact-final-window",
        ),
    ],
)
def test_chunk_text_preserves_overlap_and_terminal_boundary(text, expected):
    assert chunk_text(text, chunk_size=5, chunk_overlap=2) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param(" \t\n\r ", [], id="whitespace-only-input"),
        pytest.param("ABCD \t\n EFGH", ["ABCD", "EFGH"], id="continues-after-blank-window"),
    ],
)
def test_chunk_text_omits_blank_windows_without_losing_later_text(text, expected):
    assert chunk_text(text, chunk_size=4, chunk_overlap=0) == expected


def test_chunk_rejects_negative_index():
    with pytest.raises(ValidationError):
        Chunk(
            chunk_id="doc--1",
            doc_id="doc",
            title="Title",
            source_path="doc.md",
            chunk_index=-1,
            text="chunk",
        )
