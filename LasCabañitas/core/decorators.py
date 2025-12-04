from django.http import HttpResponseForbidden
from functools import wraps
from core.utils import get_user_role

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_role = get_user_role(request.user)
            if user_role == required_role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
        return _wrapped_view
    return decorator
