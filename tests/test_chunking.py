from app.rag.chunking import split_into_chunks


def build_text(paragraphs: int) -> str:
    return "\n\n".join(
        f"Paragraph {i}. " + "The vacation policy grants thirty days per year. " * 6
        for i in range(paragraphs)
    )


def test_short_text_becomes_a_single_chunk():
    chunks = split_into_chunks("Short text about vacation.")

    assert chunks == ["Short text about vacation."]


def test_long_text_is_split_and_respects_chunk_size():
    chunks = split_into_chunks(build_text(20), chunk_size=500, chunk_overlap=100)

    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_consecutive_chunks_share_overlapping_text():
    chunks = split_into_chunks(build_text(20), chunk_size=500, chunk_overlap=100)

    first_tail = chunks[0][-50:]
    assert first_tail in chunks[1]


def test_empty_text_returns_no_chunks():
    assert split_into_chunks("") == []