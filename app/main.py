from fastapi import FastAPI

app = FastAPI(title="rag-assistant-si-service")

@app.get("/health")
def health():
    return {"status": "ok"}

