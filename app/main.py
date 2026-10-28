import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.messaging.consumer import run_consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(run_consumer())
    yield
    consumer_task.cancel()
    with suppress(asyncio.CancelledError):
        await consumer_task


app = FastAPI(title="rag-assistant-ai-service", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}

