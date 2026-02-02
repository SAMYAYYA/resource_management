import json
from django.utils.deprecation import MiddlewareMixin
from .models import ApiHistory

class ApiHistoryMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Save body for later use so reading it here won't break views

        print("******************process_request*************")
        if request.method not in ["GET", "HEAD", "OPTIONS"]:
            try:
                request._body_copy = request.body  # store a copy
            except Exception:
                request._body_copy = b''

    def process_response(self, request, response):

        print("********************process_response***************************")
        if request.path.startswith("/management/api/"):

            # ----------- USER -----------
            user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

            # ----------- REQUEST DATA -----------
            request_data = {}
            try:
                if request.method == "GET":
                    request_data = request.GET.dict()
                elif hasattr(request, "_body_copy") and request._body_copy:
                    request_data = json.loads(request._body_copy.decode("utf-8"))
            except Exception:
                request_data = {}

            # ----------- RESPONSE DATA -----------
            response_data = {}
            try:
                # Decode JSON response safely
                response_data = json.loads(response.content)
            except Exception:
                response_data = str(response.content)

            ip_address = self.get_client_ip(request)

            # ----------- SAVE TO DB -----------
            ApiHistory.objects.create(
                user_id=getattr(user, "id", None),
                username=getattr(user, "username", None),
                api_name=request.path,
                method=request.method,
                request_data=request_data,
                response_data=response_data,
                status_code=response.status_code,

                ip_address=ip_address
            )

        return response
    
    def get_client_ip(self, request):
        """
        Retrieves client IP from headers or remote address
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # In case of multiple proxies, take the first IP
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip
