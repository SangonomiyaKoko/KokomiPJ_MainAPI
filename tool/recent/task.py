from celery import Celery

from config import settings
from log import log as logger

# 定义 Celery 实例，连接到同一个 Redis
celery_app = Celery(
    'producer',
    broker=f"pyamqp://{settings.RABBITMQ_USERNAME}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}//",  # RabbitMQ 连接地址
    broker_connection_retry_on_startup = True
)

logger.info("Celery initialization is complete")