# 目前暂时不需要该功能

# from celery import Celery

# from app.core import EnvConfig

# config = EnvConfig.get_config()

# celery_app = Celery(
#     'producer',
#     broker=f"pyamqp://{config.RABBITMQ_USERNAME}:{config.RABBITMQ_PASSWORD}@{config.RABBITMQ_HOST}//"
# )