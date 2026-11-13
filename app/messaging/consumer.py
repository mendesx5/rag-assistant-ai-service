import asyncio
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError
from pydantic import ValidationError

from app.config import settings
from app.messaging.schemas import DocumentUploadedEvent
from app.pdf.extractor import PdfExtractionError
from app.rag.pipeline import index_pdf
from app.rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)

RECONNECT_DELAY_SECONDS = 5


def process_event(body: bytes) -> int:
    """Validates the message and indexes the referenced PDF. Returns the chunk count."""
    event = DocumentUploadedEvent.model_validate_json(body)
    logger.info("Processing document %s (event %s)", event.document_id, event.event_id)
    return index_pdf(str(event.document_id), event.file_path, get_vector_store())

async def handle_message(message: AbstractIncomingMessage) -> None:
    try:
        # Reading, embedding and indexing are blocking work: run them in a thread
        # so the event loop stays free.
        chunk_count = await asyncio.to_thread(process_event, message.body)
    except (ValidationError, PdfExtractionError) as exc:
        # Irreversible: retrying will never fix it, so do NOT put it back in the queue.
        logger.error("Irreversible error, message discarded: %s", exc)
        await message.nack(requeue=False)
    except Exception:
        # Unexpected (possibly temporary): put it back in the queue.
        logger.exception("Unexpected error, message sent back to the queue")
        await message.nack(requeue=True)
    else:
        logger.info("Indexing finished (%d chunks)", chunk_count)
        # Only now, after the work succeeded, RabbitMQ is allowed to forget the message.
        await message.ack()


async def connect_with_retry() -> AbstractRobustConnection:
    while True:
        try:
            return await aio_pika.connect_robust(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                login=settings.rabbitmq_user,
                password=settings.rabbitmq_password,
            )
        except (AMQPConnectionError, OSError) as exc:
            logger.warning(
                "RabbitMQ unavailable (%s). Retrying in %ds", exc, RECONNECT_DELAY_SECONDS
            )
            await asyncio.sleep(RECONNECT_DELAY_SECONDS)


async def run_consumer() -> None:
    connection = await connect_with_retry()
    try:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(settings.rabbitmq_queue, durable=True)
        await queue.consume(handle_message)  # manual ack is the default (no_ack=False)
        logger.info("Waiting for messages on queue '%s'", settings.rabbitmq_queue)
        await asyncio.Future()  # keep running until the task is cancelled
    finally:
        await connection.close()