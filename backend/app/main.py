from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import accounts, instruments, portfolio, simulations, valuations

app = FastAPI(title="Asset Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(accounts.router, prefix="/api")
app.include_router(instruments.router, prefix="/api")
app.include_router(valuations.router, prefix="/api")
app.include_router(portfolio.router, prefix="/api")
app.include_router(simulations.router, prefix="/api")


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}
