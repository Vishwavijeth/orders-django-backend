from django.db import models

class ReportCheckpoint(models.Model):
    report_name = models.CharField(max_length=30, unique=True)
    last_order_id = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.report_name} - {self.last_order_id}"