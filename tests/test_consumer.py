import asyncio
import json
from unittest.mock import AsyncMock

from app.messaging import consumer


def make_message(file_path: str) -> AsyncMock:
    message = AsyncMock()
    message.body = json.dumps(
        {
            "event_id": "3f2b8c1e-5a4d-4e7b-9c1a-2d6f8e0b7a11",
            "document_id": "9a1c4e7d-2b3f-4d5a-8e6c-1f0a9b8c7d6e",
            "file_path": file_path,
            "timestamp": "2026-10-27T15:00:00Z",
        }
    ).encode()
    return message


def test_acks_message_after_successful_processing(make_pdf):
    message = make_message(make_pdf())

    asyncio.run(consumer.handle_message(message))

    message.ack.assert_awaited_once()
    message.nack.assert_not_awaited()


def test_discards_message_when_json_is_invalid():
    message = AsyncMock()
    message.body = b"this is not json"

    asyncio.run(consumer.handle_message(message))

    message.nack.assert_awaited_once_with(requeue=False)
    message.ack.assert_not_awaited()


def test_discards_message_when_pdf_does_not_exist(tmp_path):
    message = make_message(str(tmp_path / "missing.pdf"))

    asyncio.run(consumer.handle_message(message))

    message.nack.assert_awaited_once_with(requeue=False)
    message.ack.assert_not_awaited()


def test_requeues_message_on_unexpected_error(make_pdf, monkeypatch):
    def explode(body: bytes) -> str:
        raise RuntimeError("something unexpected")

    monkeypatch.setattr(consumer, "process_event", explode)
    message = make_message(make_pdf())

    asyncio.run(consumer.handle_message(message))

    message.nack.assert_awaited_once_with(requeue=True)
    message.ack.assert_not_awaited()