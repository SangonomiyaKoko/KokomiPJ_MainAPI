from celery import Celery

from app.core import EnvConfig
from app.core import api_logger

config = EnvConfig.get_config()

# 定义 Celery 实例，连接到同一个 Redis
celery_app = Celery(
    'producer',
    broker=f"pyamqp://{config.RABBITMQ_USERNAME}:{config.RABBITMQ_PASSWORD}@{config.RABBITMQ_HOST}//",  # RabbitMQ 连接地址
    broker_connection_retry_on_startup = True
)

api_logger.info("Celery initialization is complete")