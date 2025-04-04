from celery import Celery
from app.core import EnvConfig, api_logger

class CeleryProducer:
    """封装 Celery 任务发送，捕获错误，避免异常传播"""

    _celery_app = None

    @classmethod
    def init_celery(cls):
        """初始化 Celery 实例"""
        if cls._celery_app is not None:
            return  # 避免重复初始化

        try:
            config = EnvConfig.get_config()
            cls._celery_app = Celery(
                'producer',
                broker=f"pyamqp://{config.RABBITMQ_USERNAME}:{config.RABBITMQ_PASSWORD}@{config.RABBITMQ_HOST}//",
                broker_connection_retry_on_startup=True
            )
            api_logger.info("Celery initialization is complete")
        except Exception as e:
            api_logger.error(f"Celery initialization failed: {e}")
            cls._celery_app = None  # 确保初始化失败时，不会使用未正确初始化的实例

    @classmethod
    def send_task(cls, name: str, args: list, queue: str = 'task_queue'):
        """发送 Celery 任务，并捕获 MQ 连接异常"""
        if cls._celery_app is None:
            api_logger.error("Celery Not initialized. Call `init_celery` first.")
            return

        try:
            cls._celery_app.send_task(
                name=name, 
                args=args, 
                queue=queue
            )
            api_logger.debug(f"Task sent successfully: {name}")
        except Exception as e:
            api_logger.error(f"Failed to send task: {name}, Error: {e}")

