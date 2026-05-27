"""Root API router — mounts all v1 sub-routers."""

from fastapi import APIRouter

from app.api.v1 import auth, rooms, sessions, users, ws

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
