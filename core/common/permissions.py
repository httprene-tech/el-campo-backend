"""
Permisos compartidos para todos los módulos.
"""
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
        
        # Permitir escritura solo al creador o administradores
        is_owner = False
        if hasattr(obj, 'usuario'):
            is_owner = obj.usuario == request.user
        elif hasattr(obj, 'creado_por'):
            is_owner = obj.creado_por == request.user
            
        return is_owner or request.user.is_staff


class IsSocioActivo(permissions.BasePermission):
    """
    Permiso que verifica que el usuario tenga un perfil de socio activo.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusuarios siempre tienen permiso
        if request.user.is_superuser:
            return True
        
        # Verificar que tenga perfil de socio activo
        try:
            socio = request.user.perfil_socio
            return socio.activo
        except AttributeError:
            # Si no tiene perfil_socio, permitir acceso (compatibilidad)
            return True


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso que permite:
    - Ver el objeto (SAFE_METHODS) a cualquier usuario autenticado
    - Crear objetos a cualquier usuario autenticado
    - Modificar/Eliminar solo al dueño o administradores
    """
    def has_object_permission(self, request, view, obj):
        # Superusuarios y staff siempre tienen permiso
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        # Verificar dueño
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        if hasattr(obj, 'creado_por'):
            return obj.creado_por == request.user
            
        return False
