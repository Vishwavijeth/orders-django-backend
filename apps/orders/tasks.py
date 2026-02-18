from celery import shared_task
from .utils import OrderReportService


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def generate_order_report_task(self):
    """
    Background safe report generator
    """
    file_path, count = OrderReportService.generate_report()

    return {
        "file_path": file_path,
        "new_records": count,
    }