# tasks.py
"""
Celery异步任务模块：实现基于Celery的异步任务处理功能。
"""

from celery import Celery
import time

# 配置Celery实例
celery = Celery('tasks',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0')
# 定义异步任务
@celery.task
def process_data(data: str) -> str:
    """处理数据的异步任务"""
    time.sleep(5)  # 模拟耗时操作
    return f"处理完成: {data}"