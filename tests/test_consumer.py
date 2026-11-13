import asyncio
import json
from unittest.mock import AsyncMock

import pytest

from app.messaging import consumer

DOCUMENT_ID = "9a1c4e7d-2b3f-4d5a-8e6c-1f0a9b8c7d6e"


def make_message(file_path: str) -> AsyncMock:
    message = AsyncMock()
    message.body = json.dumps(
        {
            "event_id": "3f2b8c1e-5a4d-4e7b-9c1a-2d6f8e0b7a11",
            "document_id": DOCUMENT_ID,
            "file_path": file_path,
            "timestamp": "2026-10-27T15:00:00Z",
        }
    ).encode()
    return message


@pytest.fixture(autouse=True)
def use_test_store(store, monkeypatch):
    """Every consumer test uses the temp ChromaDB + fake embedder instead of the real ones."""
    monkeypatch.setattr(consumer, "get_vector_store", lambda: store)


def test_indexes_document_and_acks_after_success(make_pdf, store):
    message = make_message(make_pdf())

    asyncio.run(consumer.handle_message(message))

    assert store.count_chunks(DOCUMENT_ID) == 1
    message.ack.assert_awaited_once()
    message.nack.assert_not_awaited()


def test_discards_message_when_json_is_invalid():
    message = AsyncMock()
    message.body = b"this is not json"

    asyncio.run(consumer.handle_message(message))

    message.nack.assert_awaited_once_with(requeue=False)
    message.ack.assert_not_awaited()


def test_discards_message_when_pdf_does_not_exist(tmp_path, store):
    message = make_message(str(tmp_path / "missing.pdf"))

    asyncio.run(consumer.handle_message(message))

    message.nack.assert_awaited_once_with(requeue=False)
    message.ack.assert_not_awaited()
    assert store.count_chunks(DOCUMENT_ID) == 0


def test_requeues_message_when_indexing_fails_unexpectedly(make_pdf, store, monkeypatch):
    def explode(document_id, chunks):
        raise RuntimeError("vector database is down")

    monkeypatch.setattr(store, "index_document", explode)
    message = make_message(make_pdf())

    asyncio.run(consumer.handle_message(message))

    message.nack.assert_awaited_once_with(requeue=True)
    message.ack.assert_not_awaited()