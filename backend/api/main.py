from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.meetings import router as meetings_router

app = FastAPI(title="Event Sync")

# Allow the frontend (localhost:5173) to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meetings_router, prefix="/api")
