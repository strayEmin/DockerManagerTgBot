__all__ = ("router", )

from aiogram import Router

from .base import router as base_router
from .docker_commands import router as docker_router
from .unknown_commands import router as unknown_handler_router

router = Router()

router.include_router(base_router)
router.include_router(docker_router)

# этот роутер всегда должен стоять последним
router.include_router(unknown_handler_router)
