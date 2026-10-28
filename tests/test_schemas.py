import pytest
from pydantic import ValidationError

from app.messaging.schemas import DocumentUploadedEvent

VALID_JSON = (
    '{"event_id": "3f2b8c1e-5a4d-4e7b-9c1a-2d6f8e0b7a11",'
    ' "document_id": "9a1c4e7d-2b3f-4d5a-8e6c-1f0a9b8c7d6e",'
    ' "file_path": "C:\\\\uploads\\\\manual.pdf",'
    ' "timestamp": "2026-10-27T15:00:00.123456Z"}'
)


def test_parses_the_json_sent_by_the_java_api():
    event = DocumentUploadedEvent.model_validate_json(VALID_JSON)

    assert str(event.document_id) == "9a1c4e7d-2b3f-4d5a-8e6c-1f0a9b8c7d6e"
    assert event.file_path == "C:\\uploads\\manual.pdf"
    assert event.timestamp.year == 2026


def test_rejects_message_missing_required_field():
    with pytest.raises(ValidationError):
        DocumentUploadedEvent.model_validate_json('{"event_id": "not-a-uuid"}')