from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Sum
from decimal import Decimal
from core.common.models import BaseModel


# ============================================================================
# MODELOS DE CATEGORÍAS
# ============================================================================

class Categoria(BaseModel):
    """Categorías para clasificar gastos (ej: Materiales, Mano de Obra, etc.)"""
    nombre = models.CharField(max_length=100, unique=True, db_index=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f"<Categoria: {self.nombre}>"


# ============================================================================
# MODELOS DE PROVEEDORES
# ============================================================================

class Proveedor(BaseModel):
    """Proveedores de materiales y servicios"""
    nombre = models.CharField(max_length=150, unique=True, db_index=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    especialidad = models.CharField(
        max_length=100, 
        help_text="Ej: Soldadura, Materiales de construcción"
    )

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]

    @property
    def total_pagado(self):
        """Calcula el total pagado a este proveedor"""
        return self.gastos.filter(eliminado=False).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f"<Proveedor: {self.nombre} - {self.especialidad}>"


# ============================================================================
# MODELOS DE PROYECTOS
# ============================================================================

class Proyecto(BaseModel):
    """Proyectos de construcción con presupuesto asignado"""
    nombre = models.CharField(max_length=150, db_index=True)
    presupuesto_objetivo = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Presupuesto total del proyecto en Bs"
    )
    fecha_inicio = models.DateField(db_index=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['-fecha_inicio']),
            models.Index(fields=['nombre']),
        ]

    @property
    def total_gastado(self):
        """Suma total de todos los gastos del proyecto"""
        return self.gastos.filter(eliminado=False).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    @property
    def saldo_restante(self):
        """Saldo disponible del presupuesto"""
        return self.presupuesto_objetivo - self.total_gastado

    def __str__(self):
        return f"{self.nombre} - Presupuesto: {self.presupuesto_objetivo} Bs"

    def __repr__(self):
        return f"<Proyecto: {self.nombre} - Saldo: {self.saldo_restante} Bs>"


# ============================================================================
# MODELOS DE GASTOS
# ============================================================================

class Gasto(BaseModel):
    """Registro de gastos realizados en proyectos"""
    
    METODO_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('QR', 'Pago QR'),
    ]

    # Relaciones
    proyecto = models.ForeignKey(
        Proyecto, 
        on_delete=models.CASCADE, 
        related_name='gastos',
        db_index=True
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT, 
        related_name='gastos',
        db_index=True
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='gastos_registrados',
        help_text="Usuario que registró el gasto"
    )
    proveedor_rel = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='gastos',
        verbose_name="Proveedor",
        db_index=True
    )

    # Datos del gasto
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    descripcion = models.CharField(max_length=255)
    fecha = models.DateField(db_index=True)
    
    # Información de pago
    metodo_pago = models.CharField(
        max_length=20, 
        choices=METODO_PAGO, 
        default='TRANSFERENCIA',
        db_index=True
    )
    nro_referencia = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Nro de transferencia o factura"
    )

    # Metadatos
    es_retroactivo = models.BooleanField(
        default=False,
        help_text="Indica si el gasto se registró después de su fecha real"
    )
    notas_contexto = models.TextField(
        blank=True,
        help_text="Contexto adicional del gasto. Ej: 'Comprobante de retiro bancario, usado para mano de obra de cimientos'"
    )
    imagen_comprobante = models.ImageField(
        upload_to='comprobantes/%Y/%m/',
        blank=True,
        null=True,
        help_text="Foto de la factura o comprobante del gasto"
    )

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ['-fecha', '-creado_en']
        indexes = [
            models.Index(fields=['proyecto', '-fecha']),
            models.Index(fields=['categoria', '-fecha']),
            models.Index(fields=['-fecha']),
            models.Index(fields=['metodo_pago']),
        ]

    def __str__(self):
        return f"{self.fecha} | {self.monto} Bs - {self.descripcion}"

    def __repr__(self):
        return f"<Gasto: {self.monto} Bs - {self.categoria.nombre}>"


class Comprobante(BaseModel):
    """Fotos/imágenes de comprobantes de gastos"""
    gasto = models.ForeignKey(
        Gasto, 
        on_delete=models.CASCADE, 
        related_name='fotos',
        db_index=True
    )
    imagen = models.ImageField(upload_to='comprobantes/%Y/%m/')

    class Meta:
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['gasto', '-creado_en']),
        ]

    def __str__(self):
        return f"Comprobante de gasto: {self.gasto.id}"

    def __repr__(self):
        return f"<Comprobante: Gasto #{self.gasto.id}>"


# ============================================================================
# MODELOS DE SOCIOS/FAMILIA
# ============================================================================

class Socio(BaseModel):
    """
    Perfil extendido para socios/familia del proyecto.
    Cada miembro de la familia que participa en el proyecto tiene un perfil.
    """
    ROLES = [
        ('ADMINISTRADOR', 'Administrador'),  # Puede todo
        ('REGISTRADOR', 'Registrador'),       # Registrar gastos y subir archivos
        ('VISUALIZADOR', 'Visualizador'),     # Solo consultar
    ]

    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='perfil_socio'
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='REGISTRADOR')
    telefono = models.CharField(max_length=20, blank=True)
    parentesco = models.CharField(
        max_length=50, 
        help_text="Relación familiar. Ej: Hermana, Cuñado, Madre"
    )
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Si está activo puede acceder al sistema"
    )

    class Meta:
        verbose_name = "Socio"
        verbose_name_plural = "Socios"
        ordering = ['usuario__first_name']
        indexes = [
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.parentesco})"

    def __repr__(self):
        return f"<Socio: {self.usuario.username} - {self.rol}>"


# ============================================================================
# MODELOS DE GALERÍA DE IMÁGENES
# ============================================================================

class Album(BaseModel):
    """
    Álbumes para organizar fotos del proyecto.
    Ej: "Cimientos", "Estructura", "Techado", "Terminado"
    """
    nombre = models.CharField(max_length=100, db_index=True)
    descripcion = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='albums_creados',
        db_index=True
    )

    class Meta:
        verbose_name = "Álbum"
        verbose_name_plural = "Álbumes"
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['-creado_en']),
        ]

    @property
    def cantidad_fotos(self):
        """Retorna la cantidad de fotos en el álbum"""
        return self.fotos.filter(eliminado=False).count()

    def __str__(self):
        return f"{self.nombre} ({self.cantidad_fotos} fotos)"

    def __repr__(self):
        return f"<Album: {self.nombre}>"


class FotoAlbum(BaseModel):
    """Fotos dentro de un álbum de la galería"""
    album = models.ForeignKey(
        Album, 
        on_delete=models.CASCADE, 
        related_name='fotos',
        db_index=True
    )
    imagen = models.ImageField(upload_to='galeria/%Y/%m/')
    titulo = models.CharField(max_length=100, blank=True)
    descripcion = models.CharField(max_length=255, blank=True)
    fecha_foto = models.DateField(
        null=True, 
        blank=True,
        db_index=True,
        help_text="Fecha en que se tomó la foto"
    )
    subido_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='fotos_subidas',
        db_index=True
    )

    class Meta:
        verbose_name = "Foto"
        verbose_name_plural = "Fotos"
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['album', '-creado_en']),
            models.Index(fields=['fecha_foto']),
        ]

    def __str__(self):
        return self.titulo or f"Foto {self.id} - {self.album.nombre}"

    def __repr__(self):
        return f"<FotoAlbum: {self.id} en {self.album.nombre}>"


# ============================================================================
# MODELOS DE DOCUMENTOS
# ============================================================================

class CarpetaDocumento(BaseModel):
    """
    Carpetas para organizar documentos.
    Ej: "Plan de Pago Banco", "Contratos", "Facturas", "Permisos"
    """
    nombre = models.CharField(max_length=100, unique=True, db_index=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(
        max_length=50, 
        default='folder',
        help_text="Nombre del ícono para el frontend"
    )

    class Meta:
        verbose_name = "Carpeta de Documentos"
        verbose_name_plural = "Carpetas de Documentos"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]

    @property
    def cantidad_documentos(self):
        """Retorna la cantidad de documentos en la carpeta"""
        return self.documentos.filter(eliminado=False).count()

    def __str__(self):
        return f"📁 {self.nombre}"

    def __repr__(self):
        return f"<CarpetaDocumento: {self.nombre}>"


class Documento(BaseModel):
    """
    Documentos del proyecto.
    Ej: Plan de pago del banco, contratos, facturas, comprobantes, etc.
    """
    TIPOS = [
        ('PLAN_PAGO', 'Plan de Pago'),
        ('CONTRATO', 'Contrato'),
        ('COMPROBANTE_BANCO', 'Comprobante Bancario'),
        ('FACTURA', 'Factura'),
        ('PERMISO', 'Permiso Municipal'),
        ('PLANO', 'Plano/Diseño'),
        ('OTRO', 'Otro'),
    ]

    carpeta = models.ForeignKey(
        CarpetaDocumento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='documentos',
        db_index=True
    )
    tipo = models.CharField(
        max_length=20, 
        choices=TIPOS, 
        default='OTRO',
        db_index=True
    )
    nombre = models.CharField(max_length=150, db_index=True)
    archivo = models.FileField(upload_to='documentos/%Y/%m/')
    descripcion = models.TextField(blank=True)
    fecha_documento = models.DateField(
        db_index=True,
        help_text="Fecha del documento (no de subida)"
    )
    subido_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='documentos_subidos',
        db_index=True
    )

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-fecha_documento']
        indexes = [
            models.Index(fields=['-fecha_documento']),
            models.Index(fields=['tipo', '-fecha_documento']),
            models.Index(fields=['carpeta', '-fecha_documento']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nombre}"

    def __repr__(self):
        return f"<Documento: {self.nombre} ({self.tipo})>"