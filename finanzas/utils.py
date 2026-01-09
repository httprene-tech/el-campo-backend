"""
Utilidades y funciones helper para el módulo de finanzas.
"""
import io
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def generar_reporte_proyecto_pdf(proyecto, gastos):
    """
    Genera un reporte PDF para un proyecto específico.
    
    Args:
        proyecto: Instancia del modelo Proyecto
        gastos: QuerySet de Gastos del proyecto
    
    Returns:
        BytesIO: Buffer con el contenido del PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título y Encabezado
    elements.append(Paragraph(f"Reporte de Inversión: {proyecto.nombre}", styles['Title']))
    elements.append(Paragraph(
        f"Presupuesto Total: {proyecto.presupuesto_objetivo} Bs | "
        f"Total Gastado: {proyecto.total_gastado} Bs | "
        f"Saldo Disponible: {proyecto.saldo_restante} Bs",
        styles['Normal']
    ))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Tabla de Gastos
    data = [['Fecha', 'Descripción', 'Categoría', 'Proveedor', 'Monto (Bs)']]
    for g in gastos:
        proveedor_nombre = g.proveedor_rel.nombre if g.proveedor_rel else 'N/A'
        data.append([
            g.fecha.strftime('%d/%m/%Y'),
            g.descripcion[:25],  # Acortar para que quepa
            g.categoria.nombre,
            proveedor_nombre[:20],
            f"{g.monto:.2f}"
        ])

    # Fila de totales
    data.append(['', '', '', 'TOTAL:', f"{proyecto.total_gastado:.2f}"])

    # Estilo de la tabla
    tabla = Table(data, colWidths=[70, 150, 90, 100, 70])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(tabla)
    doc.build(elements)

    buffer.seek(0)
    return buffer


def calcular_porcentaje_consumido(total_gastado, presupuesto_objetivo):
    """
    Calcula el porcentaje consumido del presupuesto.
    
    Args:
        total_gastado: Decimal con el total gastado
        presupuesto_objetivo: Decimal con el presupuesto objetivo
    
    Returns:
        float: Porcentaje consumido (0-100)
    """
    if presupuesto_objetivo > 0:
        porcentaje = (total_gastado / presupuesto_objetivo) * 100
        return round(float(porcentaje), 2)
    return 0.0


def verificar_stock_bajo(material):
    """
    Verifica si un material tiene stock bajo.
    DEPRECATED: Usar inventario.services.InventarioService.obtener_materiales_stock_bajo()
    
    Args:
        material: Instancia del modelo Material (de inventario)
    
    Returns:
        bool: True si el stock está en nivel de alerta
    """
    from inventario.models import Material
    if isinstance(material, Material):
        return material.stock_actual <= material.stock_minimo_alerta
    return False


def obtener_materiales_stock_bajo():
    """
    Obtiene todos los materiales con stock bajo.
    
    Returns:
        QuerySet: Materiales con stock bajo
    """
    from inventario.models import Material
    from django.db.models import F
    
    return Material.objects.filter(
        eliminado=False,
        stock_actual__lte=F('stock_minimo_alerta')
    )


def formatear_monto_boliviano(monto):
    """
    Formatea un monto en bolivianos.
    
    Args:
        monto: Decimal o float con el monto
    
    Returns:
        str: Monto formateado (ej: "1,234.56 Bs")
    """
    return f"{monto:,.2f} Bs".replace(',', 'X').replace('.', ',').replace('X', '.')


def calcular_gasto_por_categoria(proyecto):
    """
    Calcula el total gastado por categoría para un proyecto.
    
    Args:
        proyecto: Instancia del modelo Proyecto
    
    Returns:
        dict: Diccionario con categoría como key y monto total como value
    """
    from django.db.models import Sum
    
    gastos_por_categoria = proyecto.gastos.values(
        'categoria__nombre'
    ).annotate(
        total=Sum('monto')
    ).order_by('-total')
    
    return {
        item['categoria__nombre']: item['total'] 
        for item in gastos_por_categoria
    }
