from .models import ApiHistory

def log_api_history(request, api_name, response_data, status_code):
    user = request.user if request.user.is_authenticated else None

    ApiHistory.objects.create(
        user_id=getattr(user, "id", None),
        username=getattr(user, "username", None),
        api_name=api_name,
        method=request.method,
        request_data=request.data if request.method == "POST" else request.GET.dict(),
        response_data=response_data,
        status_code=status_code
    )
