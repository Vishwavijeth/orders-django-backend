from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from ..tasks import generate_order_report_task
from django.conf import settings
from rest_framework.response import Response

class GenerateOrderReportAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        task = generate_order_report_task.delay()

        file_url = request.build_absolute_uri(
            settings.MEDIA_URL + "order_details_report.xlsx"
        )

        return Response({
            "message": "report generation started",
            "task id": task.id,
            "file_url": file_url
        })