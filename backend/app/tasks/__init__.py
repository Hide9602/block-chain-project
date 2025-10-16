"""
Celery tasks module for asynchronous processing
"""
from .celery_app import celery_app
from .report_tasks import generate_report_task

__all__ = ["celery_app", "generate_report_task"]
