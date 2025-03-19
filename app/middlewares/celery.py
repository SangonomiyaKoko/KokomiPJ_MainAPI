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

class CeleryProducer:
    """封装 Celery 任务发送，捕获错误，避免异常传播"""
    @staticmethod
    def send_task(name: str, args: list, queue: str = 'task_queue'):
        """发送 Celery 任务，并捕获 MQ 连接异常"""
        try:
            celery_app.send_task(
                name=name,
                args=args,
                queue=queue
            )
            api_logger.debug(f"Celery: Task sent successfully: {name}")
        except Exception as e:
            api_logger.error(f"Celery: Failed to send task: {name}")