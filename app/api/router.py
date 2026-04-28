from fastapi import APIRouter

from app.api.routes import analytics, applications, auth, notes, reminders

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(applications.router)
api_router.include_router(notes.router)
api_router.include_router(reminders.router)
api_router.include_router(analytics.router)
