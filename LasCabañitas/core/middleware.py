from django.shortcuts import redirect
from core.utils import get_user_role

class RoleRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path == "/accounts/profile/":
            role = get_user_role(request.user)
            if role == "Administrador":
                return redirect("/dashboard/admin/")
            elif role == "Encargado":
                return redirect("/dashboard/manager/")
            else:
                return redirect("/dashboard/default/")

        return response
