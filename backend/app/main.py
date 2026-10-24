from fastapi import FastAPI

app = FastAPI(title="HealthTrack")


@app.get("/api/health")
def health():
    return {"status": "ok"}