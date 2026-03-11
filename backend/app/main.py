from fastapi import FastAPI

from backend.app.api.routes.analyze import router as analyze_router
from backend.app.api.routes.watchlist import router as watchlist_router

app = FastAPI()
app.include_router(analyze_router)
app.include_router(watchlist_router)
