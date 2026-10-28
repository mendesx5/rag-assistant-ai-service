from app.config import Settings


def test_settings_use_defaults_when_env_is_empty(monkeypatch):
    monkeypatch.delenv("RABBITMQ_HOST", raising=False)

    settings = Settings(_env_file=None)

    assert settings.rabbitmq_host == "localhost"
    assert settings.rabbitmq_queue == "documents.queue"


def test_settings_read_values_from_environment(monkeypatch):
    monkeypatch.setenv("RABBITMQ_HOST", "rabbit.internal")
    monkeypatch.setenv("RABBITMQ_PORT", "5673")

    settings = Settings(_env_file=None)

    assert settings.rabbitmq_host == "rabbit.internal"
    assert settings.rabbitmq_port == 5673