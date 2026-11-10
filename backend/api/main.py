from fastapi import FastAPI

from api.meetings import router as meetings_router

app = FastAPI(title="Event Sync")
app.include_router(meetings_router, prefix="/api")
