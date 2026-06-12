"""Сборка всех роутеров сервиса в единый APIRouter"""

from fastapi import APIRouter

from app.api import routes_auth

api_router = APIRouter()
api_router.include_router(routes_auth.router)
