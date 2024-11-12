from .platfrom_urls import router as platform_router
from .robot_urls import router as robot_router
from .recent_urls import router as recent_1_router

__all__ = [
    'platform_router',
    'robot_router',
    'recent_1_router'
]