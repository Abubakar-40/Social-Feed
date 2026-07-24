import logging
import time

from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger("config.request")


class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - getattr(request, "start_time", time.time())
        logger.info("%s %s %s %.3fs", request.method, request.path, response.status_code, duration)

        return response
