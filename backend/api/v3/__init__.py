"""
V3 API Module - Scientific calculations and enhanced features for TENAX FIT
"""
from fastapi import APIRouter
from . import calculations, safety

# Create main v3 router
v3_router = APIRouter(prefix="/api/v3", tags=["V3 API"])

# Include sub-routers
v3_router.include_router(
    calculations.router,
    prefix="/calculations",
    tags=["Scientific Calculations"]
)

v3_router.include_router(
    safety.router,
    prefix="/safety",
    tags=["Health & Safety"]
)

__all__ = ["v3_router"]