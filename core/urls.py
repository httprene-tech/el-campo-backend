from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
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