from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite:
    - Cualquier usuario autenticado puede leer (GET, HEAD, OPTIONS)
    - Solo administradores pueden modificar (POST, PUT, PATCH, DELETE)
    """
    def has_permission(self, request, view):
        # Permitir lectura a todos los usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Permitir escritura solo a administradores
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite:
    - El creador del objeto puede editarlo
    - Otros usuarios solo pueden leerlo
    """
    def has_object_permission(self, request, view, obj):
        # Permitir lectura a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permitir escritura solo al creador (si el objeto tiene campo 'usuario')
        return obj.usuario == request.user if hasattr(obj, 'usuario') else False


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):
    """
    Permiso que permite crear objetos sin autenticación,
    pero requiere autenticación para otras operaciones.
    Útil para registro de usuarios.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user and request.user.is_authenticated
