from fastapi import FastAPI

from backend.app.api.routes.analyze import router as analyze_router
from backend.app.api.routes.watchlist import router as watchlist_router
from backend.app.api.routes.sessions import router as sessions_router

app = FastAPI()
app.include_router(analyze_router)
app.include_router(watchlist_router)
app.include_router(sessions_router)
