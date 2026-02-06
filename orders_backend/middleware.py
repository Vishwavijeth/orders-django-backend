import logging

logger = logging.getLogger("django")

class RequestResponseLoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log incoming request
        self.log_request(request)

        # Process request
        response = self.get_response(request)

        # Log outgoing response
        self.log_response(request, response)

        return response

    def log_request(self, request):
        try:
            body = request.body.decode("utf-8") if request.body else ""
        except Exception:
            body = "<could not decode>"

        logger.info(
            f"Incoming Request | Method: {request.method} | Path: {request.path} | "
            f"Query Params: {request.GET.dict()} | Body: {body}"
        )

    def log_response(self, request, response):
        try:
            content = response.content.decode("utf-8") if hasattr(response, "content") else "<streaming>"
        except Exception:
            content = "<could not decode>"

        logger.info(
            f"Outgoing Response | Method: {request.method} | Path: {request.path} | "
            f"Status: {response.status_code} | Response: {content}"
        )
