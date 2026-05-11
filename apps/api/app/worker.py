from celery import Celery

from app.config import settings

celery_app = Celery(
    "colossus",
    broker=settings.redis_url,
    backend=settings.redis_url,
    # Task modules are added here as they are created:
    # include=["app.tasks.video", "app.tasks.progression"],
    include=[],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Retry policy
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
