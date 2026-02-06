from celery import shared_task
from .utils import send_email

@shared_task(bind=True, autoretry_for=(Exception, ), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_user_verify_mail(self, verification_link, email):
    send_email(
            subject="Verify your email",
            message=f"Click the link to verify your email {verification_link}",
            recipient=email
    )