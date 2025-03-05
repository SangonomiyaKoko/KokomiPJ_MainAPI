from .platform_urls import router as platform_router
from .robot_urls import router as robot_router
from .recent_urls import router as recent_1_router
from .root_urls import router as root_router
from .rank_urls import router as rank_router
from .software_urls import router as software_router

__all__ = [
    'platform_router',
    'robot_router',
    'recent_1_router',
    'root_router',
    'rank_router',
    'software_router'
]