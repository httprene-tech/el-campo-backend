from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Finanzas
    ProyectoViewSet, CategoriaViewSet, GastoViewSet, ProveedorViewSet,
    # Socios/Familia
    SocioViewSet,
    # Galería
    AlbumViewSet, FotoAlbumViewSet,
    # Documentos
    CarpetaDocumentoViewSet, DocumentoViewSet,
    # Auth
    CustomAuthToken, CambiarContrasenaView
)

# Router para los endpoints REST
router = DefaultRouter()

# Finanzas
router.register(r'proyectos', ProyectoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'gastos', GastoViewSet)
router.register(r'proveedores', ProveedorViewSet)

# Socios/Familia
router.register(r'socios', SocioViewSet)

# Galería
router.register(r'albumes', AlbumViewSet)
router.register(r'fotos', FotoAlbumViewSet)

# Documentos
router.register(r'carpetas', CarpetaDocumentoViewSet)
router.register(r'documentos', DocumentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('auth/cambiar-contrasena/', CambiarContrasenaView.as_view(), name='cambiar_contrasena'),
]

