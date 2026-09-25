"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from routes.leagues import router as leagues_router
from routes.calculate import router as calculate_router
from routes.results import router as results_router

app = FastAPI(title="FF Luck Calculator API")

# CORS is largely handled by Vercel's proxy rewrites, but allow all origins
# here to support local development against the backend directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(leagues_router, prefix="/api")
app.include_router(calculate_router, prefix="/api")
app.include_router(results_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
