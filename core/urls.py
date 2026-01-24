from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from finanzas.views import CustomAuthToken, CambiarContrasenaView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Documentación API (Swagger/ReDoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Autenticación global
    path('api/auth/login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('api/auth/cambiar-contrasena/', CambiarContrasenaView.as_view(), name='cambiar_contrasena'),
    # Compatibilidad con frontend antiguo
    path('api/finanzas/auth/login/', CustomAuthToken.as_view()),
    path('api/finanzas/auth/cambiar-contrasena/', CambiarContrasenaView.as_view()),
    # Módulos del ERP
    path('api/finanzas/', include('finanzas.urls')),
    path('api/inventario/', include('inventario.urls')),
    path('api/calendario/', include('calendario.urls')),
    path('api/produccion/', include('produccion.urls')),
    path('api/salud/', include('salud.urls')),
    path('api/alimentacion/', include('alimentacion.urls')),
]

# Esto permite ver las fotos de los recibos en el navegador durante desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)