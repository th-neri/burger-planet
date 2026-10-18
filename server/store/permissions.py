from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        # anyone can access the endpoint as long as the method(GET in this case) is in SAFE_METHODS
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff) # if request user is set and if the user is staff then return true