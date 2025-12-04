from django.contrib.auth.views import LoginView
from core.utils import get_user_role

class CustomLoginView(LoginView):
    template_name = "core/login.html" 

    def get_success_url(self):
        role = get_user_role(self.request.user)
        if role == "Administrador":
            return "/dashboard/admin/"
        elif role == "Encargado":
            return "/dashboard/manager/"
        else:
            return "/dashboard/default/"
