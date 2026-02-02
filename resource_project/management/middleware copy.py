import json
from .models import ApiHistory

# class ApiHistoryMiddleware:

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)

#         if request.path.startswith("/management/api/"):
#             print(request.user)
#             user = request.user if request.user.is_authenticated else None

#             # ---------- REQUEST DATA ----------
#             request_data = None

#             if request.method == "GET":
#                 request_data = request.GET.dict()
#             else:
#                 try:
#                     if request.body:
#                         request_data = json.loads(request.body.decode("utf-8"))
#                 except Exception:
#                     request_data = None

#             # ---------- RESPONSE DATA ----------
#             try:
#                 response_data = json.loads(response.content)
#             except Exception:
#                 response_data = None

#             ApiHistory.objects.create(
#                 user_id=getattr(user, "id", None),
#                 username=getattr(user, "username", None),
#                 api_name=request.path,
#                 method=request.method,
#                 request_data=request_data,
#                 response_data=response_data,
#                 status_code=response.status_code
#             )

#         return response




class ApiHistoryMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not request.path.startswith("/management/api/"):
            return response

        

        user = request.user if request.user.is_authenticated else None

        request_data = {}

        print("*****************************",request_data)
        try:
            if request.method in ("POST", "PUT", "PATCH"):
                request_data = json.loads(request.body.decode("utf-8"))

                print("*****************************",request_data)
            else:
                request_data = request.GET.dict()
        except Exception as e:
            print("&&&&&&&&&&&&&&&&&",e)
            request_data = {}

        # RESPONSE DATA
        try:
            response_data = json.loads(response.content.decode("utf-8"))
        except:
            response_data = None

        ApiHistory.objects.create(
            user_id=getattr(user, "id", None),
            username=getattr(user, "username", None),
            api_name=request.path,
            method=request.method,
            request_data=request_data,
            response_data=response_data,
            status_code=response.status_code
        )

        return response

