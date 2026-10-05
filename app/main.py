from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from buyer.agent import execute
from buyer.cli import _fixture_for, recorded_run


app = FastAPI(title="Gecko Buyer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PurchaseRequest(BaseModel):
    ask: str


@app.get("/")
def home():
    return {
        "name": "Gecko Buyer",
        "status": "running",
        "message": "Gecko Buyer API is alive 🦎",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check")
def check_purchase(request: PurchaseRequest):
    try:
        fixture = _fixture_for(request.ask)

        run = recorded_run(
            fixture,
            Path(".recorded"),
        )

        outcome = execute(run)

        return {
            "ok": True,
            "ask": request.ask,
            "source": run.source,
            "outcome": outcome.to_json(),
        }

    except SystemExit as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )