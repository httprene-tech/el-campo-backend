# Standard library imports
import io
import logging
from datetime import datetime, timedelta

# Django imports
from django.http import FileResponse
from django.contrib.auth.models import User
from django.db.models import Sum

# Django REST Framework imports
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser

# ReportLab imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Local imports
from .models import (
    Proyecto, Categoria, Gasto, Proveedor, Material, MovimientoInventario,
    Socio, Album, FotoAlbum, CarpetaDocumento, Documento
)
from .serializers import (
    ProyectoSerializer, CategoriaSerializer, GastoSerializer, ProveedorSerializer,
    MaterialSerializer, MovimientoInventarioSerializer,
    SocioSerializer, AlbumSerializer, AlbumListSerializer, FotoAlbumSerializer,
    CarpetaDocumentoSerializer, CarpetaDocumentoListSerializer, DocumentoSerializer
)
from .constants import ERROR_PRESUPUESTO_EXCEDIDO
from .permissions import IsAdminOrReadOnly

# Logger configuration
logger = logging.getLogger(__name__)


class CustomAuthToken(ObtainAuthToken):
    """
    Vista personalizada para autenticación que retorna token + datos de usuario + perfil socio.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Obtener perfil de socio si existe
        perfil_socio = None
        try:
            socio = user.perfil_socio
            perfil_socio = {
                'rol': socio.rol,
                'parentesco': socio.parentesco,
                'activo': socio.activo
            }
        except Socio.DoesNotExist:
            pass
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'roles': [group.name for group in user.groups.all()],
            'perfil_socio': perfil_socio
        })


from rest_framework.views import APIView

class CambiarContrasenaView(APIView):
    """
    Vista para cambiar la contraseña del usuario autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response(
                {'error': 'Se requiere la contraseña actual y la nueva'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar contraseña actual
        if not user.check_password(current_password):
            return Response(
                {'error': 'La contraseña actual es incorrecta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Contraseña cambiada correctamente'})


# ============================================================================
# VIEWSETS DE SOCIOS/FAMILIA
# ============================================================================

class SocioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar socios/familia del proyecto.
    Solo administradores pueden crear/editar/eliminar socios.
    """
    queryset = Socio.objects.filter(activo=True)
    serializer_class = SocioSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


# ============================================================================
# VIEWSETS DE GALERÍA
# ============================================================================

class AlbumViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar álbumes de fotos.
    """
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Usa serializer ligero para listado."""
        if self.action == 'list':
            return AlbumListSerializer
        return AlbumSerializer

    def perform_create(self, serializer):
        """Asigna el usuario que crea el álbum."""
        serializer.save(creado_por=self.request.user)


class FotoAlbumViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar fotos dentro de álbumes.
    """
    queryset = FotoAlbum.objects.all()
    serializer_class = FotoAlbumSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Permite filtrar fotos por álbum."""
        queryset = FotoAlbum.objects.all()
        album_id = self.request.query_params.get('album', None)
        if album_id:
            queryset = queryset.filter(album_id=album_id)
        return queryset

    def perform_create(self, serializer):
        """Asigna el usuario que sube la foto."""
        serializer.save(subido_por=self.request.user)


# ============================================================================
# VIEWSETS DE DOCUMENTOS
# ============================================================================

class CarpetaDocumentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar carpetas de documentos.
    """
    queryset = CarpetaDocumento.objects.all()
    serializer_class = CarpetaDocumentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Usa serializer ligero para listado."""
        if self.action == 'list':
            return CarpetaDocumentoListSerializer
        return CarpetaDocumentoSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar documentos.
    """
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Permite filtrar documentos por carpeta y tipo."""
        queryset = Documento.objects.all()
        carpeta_id = self.request.query_params.get('carpeta', None)
        tipo = self.request.query_params.get('tipo', None)
        
        if carpeta_id:
            queryset = queryset.filter(carpeta_id=carpeta_id)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset

    def perform_create(self, serializer):
        """Asigna el usuario que sube el documento."""
        serializer.save(subido_por=self.request.user)


# ============================================================================
# VIEWSETS DE INVENTARIO
# ============================================================================

class MaterialViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar materiales de construcción."""
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]


class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    """ViewSet para registrar movimientos de inventario."""
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]


# ============================================================================
# VIEWSETS DE PROVEEDORES
# ============================================================================

class ProveedorViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar proveedores."""
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]


# ============================================================================
# VIEWSETS DE PROYECTOS
# ============================================================================

class ProyectoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar proyectos de construcción.
    Incluye endpoint personalizado para exportar reportes en PDF.
    """
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def exportar_pdf(self, request, pk=None):
        """
        Genera un reporte PDF del proyecto con filtros opcionales.
        
        Query params:
            - fecha_inicio: Fecha inicio del filtro (YYYY-MM-DD)
            - fecha_fin: Fecha fin del filtro (YYYY-MM-DD)
            - categoria: ID de categoría a filtrar
            - mes_actual: Si es 'true', filtra solo el mes actual
            - mes_anterior: Si es 'true', filtra solo el mes anterior
        """
        proyecto = self.get_object()
        gastos = Gasto.objects.filter(proyecto=proyecto).order_by('fecha')

        # Aplicar filtros
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        categoria_id = request.query_params.get('categoria')
        mes_actual = request.query_params.get('mes_actual', '').lower() == 'true'
        mes_anterior = request.query_params.get('mes_anterior', '').lower() == 'true'

        # Filtro por mes actual
        if mes_actual:
            hoy = datetime.now()
            fecha_inicio = hoy.replace(day=1).strftime('%Y-%m-%d')
            fecha_fin = hoy.strftime('%Y-%m-%d')

        # Filtro por mes anterior
        if mes_anterior:
            hoy = datetime.now()
            primer_dia_mes_actual = hoy.replace(day=1)
            ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
            primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
            fecha_inicio = primer_dia_mes_anterior.strftime('%Y-%m-%d')
            fecha_fin = ultimo_dia_mes_anterior.strftime('%Y-%m-%d')

        if fecha_inicio:
            gastos = gastos.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            gastos = gastos.filter(fecha__lte=fecha_fin)
        if categoria_id:
            gastos = gastos.filter(categoria_id=categoria_id)

        # Crear el buffer en memoria
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Título y Encabezado
        elements.append(Paragraph(f"Reporte de Inversión: {proyecto.nombre}", styles['Title']))
        elements.append(Paragraph(f"Presupuesto Total: {proyecto.presupuesto_objetivo:,.2f} Bs", styles['Normal']))
        elements.append(Paragraph(f"Total Gastado: {proyecto.total_gastado:,.2f} Bs", styles['Normal']))
        elements.append(Paragraph(f"Saldo Disponible: {proyecto.saldo_restante:,.2f} Bs", styles['Normal']))
        
        # Mostrar filtros aplicados
        if fecha_inicio or fecha_fin or categoria_id:
            filtros = []
            if fecha_inicio:
                filtros.append(f"Desde: {fecha_inicio}")
            if fecha_fin:
                filtros.append(f"Hasta: {fecha_fin}")
            if categoria_id:
                try:
                    cat = Categoria.objects.get(pk=categoria_id)
                    filtros.append(f"Categoría: {cat.nombre}")
                except Categoria.DoesNotExist:
                    pass
            elements.append(Paragraph(f"Filtros: {', '.join(filtros)}", styles['Italic']))

        elements.append(Spacer(1, 20))

        # Resumen por Categoría
        resumen_categorias = gastos.values('categoria__nombre').annotate(
            total=Sum('monto')
        ).order_by('-total')

        if resumen_categorias:
            elements.append(Paragraph("Resumen por Categoría", styles['Heading2']))
            data_resumen = [['Categoría', 'Total (Bs)']]
            for cat in resumen_categorias:
                data_resumen.append([cat['categoria__nombre'], f"{cat['total']:,.2f}"])
            
            tabla_resumen = Table(data_resumen, colWidths=[300, 150])
            tabla_resumen.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(tabla_resumen)
            elements.append(Spacer(1, 20))

        # Tabla de Gastos Detallados
        elements.append(Paragraph("Detalle de Gastos", styles['Heading2']))
        data = [['Fecha', 'Descripción', 'Categoría', 'Monto (Bs)']]
        total_filtrado = 0
        for g in gastos:
            data.append([
                g.fecha.strftime('%d/%m/%Y'),
                g.descripcion[:35],
                g.categoria.nombre,
                f"{g.monto:,.2f}"
            ])
            total_filtrado += g.monto

        # Fila de total
        data.append(['', '', 'TOTAL:', f"{total_filtrado:,.2f}"])

        # Estilo de la tabla
        tabla = Table(data, colWidths=[70, 230, 100, 80])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(tabla)
        doc.build(elements)

        buffer.seek(0)
        
        # Nombre del archivo con filtros
        nombre_archivo = f'Reporte_{proyecto.nombre}'
        if mes_actual:
            nombre_archivo += '_MesActual'
        elif mes_anterior:
            nombre_archivo += '_MesAnterior'
        
        return FileResponse(buffer, as_attachment=True, filename=f'{nombre_archivo}.pdf')


# ============================================================================
# VIEWSETS DE CATEGORÍAS
# ============================================================================

class CategoriaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar categorías de gastos."""
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]


# ============================================================================
# VIEWSETS DE GASTOS
# ============================================================================

class GastoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para registrar y gestionar gastos del proyecto.
    Incluye validaciones automáticas de presupuesto y filtros.
    """
    queryset = Gasto.objects.all()
    serializer_class = GastoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Permite filtrar gastos por proyecto, categoría, fecha y retroactivo."""
        queryset = Gasto.objects.all()
        
        proyecto_id = self.request.query_params.get('proyecto')
        categoria_id = self.request.query_params.get('categoria')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        es_retroactivo = self.request.query_params.get('es_retroactivo')
        
        if proyecto_id:
            queryset = queryset.filter(proyecto_id=proyecto_id)
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        if es_retroactivo is not None:
            queryset = queryset.filter(es_retroactivo=es_retroactivo.lower() == 'true')
            
        return queryset

    def perform_create(self, serializer):
        """Inyecta el usuario que registra el gasto."""
        serializer.save(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        """Valida que no se exceda el presupuesto del proyecto."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        proyecto = serializer.validated_data['proyecto']
        monto_nuevo = serializer.validated_data['monto']
        
        if proyecto.total_gastado + monto_nuevo > proyecto.presupuesto_objetivo:
            logger.warning(
                f'Intento de gasto que excede presupuesto: Proyecto={proyecto.nombre}, '
                f'Monto={monto_nuevo}, Saldo disponible={proyecto.saldo_restante}'
            )
            return Response(
                {
                    "error": ERROR_PRESUPUESTO_EXCEDIDO,
                    "detalle": {
                        "presupuesto_total": str(proyecto.presupuesto_objetivo),
                        "total_gastado": str(proyecto.total_gastado),
                        "saldo_disponible": str(proyecto.saldo_restante),
                        "monto_solicitado": str(monto_nuevo)
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_create(serializer)
        logger.info(
            f'Gasto creado exitosamente: {monto_nuevo} Bs en proyecto {proyecto.nombre}'
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def resumen_mensual(self, request):
        """
        Retorna un resumen de gastos agrupado por mes.
        Query params:
            - proyecto: ID del proyecto (requerido)
        """
        proyecto_id = request.query_params.get('proyecto')
        if not proyecto_id:
            return Response(
                {"error": "Se requiere el parámetro 'proyecto'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.db.models.functions import TruncMonth
        
        gastos = Gasto.objects.filter(proyecto_id=proyecto_id)
        resumen = gastos.annotate(
            mes=TruncMonth('fecha')
        ).values('mes').annotate(
            total=Sum('monto')
        ).order_by('-mes')
        
        return Response(list(resumen))