from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "portfolio"):
            return obj.portfolio.user == request.user
        return False


class IsProUser(BasePermission):
    message = "Questa funzionalità è riservata agli utenti Pro."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "pro"
        )