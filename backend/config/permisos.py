from rest_framework.permissions import BasePermission, SAFE_METHODS
def rol_de(request):
    u = request.user
    return getattr(u, "rol", None) if u and u.is_authenticated else None
def roles_permitidos(*roles, solo_escritura=True):
    """Fabrica un permiso: lectura para cualquier autenticado, escritura solo para `roles`."""
    class Permiso(BasePermission):
        message = "No tiene permiso para realizar esta acción con su rol."
        def has_permission(self, request, view):
            if not (request.user and request.user.is_authenticated):
                return False
            if solo_escritura and request.method in SAFE_METHODS:
                return True
            return rol_de(request) in roles
    return Permiso