"""
Servicios de lógica de negocio para el módulo de inventario.
"""
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import F
from .models import Material, MovimientoInventario
from .exceptions import StockInsuficienteError


class InventarioService:
    """Servicio para operaciones de inventario."""
    
    @staticmethod
    @transaction.atomic
    def actualizar_stock(material: Material, cantidad: Decimal, tipo_movimiento: str) -> Material:
        """
        Actualiza el stock de un material de forma segura.
        
        Args:
            material: Instancia de Material
            cantidad: Cantidad a agregar o restar
            tipo_movimiento: 'ENTRADA', 'SALIDA' o 'AJUSTE'
            
        Returns:
            Material: Material actualizado
            
        Raises:
            StockInsuficienteError: Si no hay stock suficiente para salida
        """
        # Bloquear el material para evitar race conditions
        material = Material.objects.select_for_update().get(pk=material.pk)
        
        if tipo_movimiento == 'ENTRADA':
            material.stock_actual += cantidad
        elif tipo_movimiento == 'SALIDA':
            nuevo_stock = material.stock_actual - cantidad
            if nuevo_stock < 0:
                raise StockInsuficienteError(
                    material=material,
                    cantidad_solicitada=cantidad,
                    stock_disponible=material.stock_actual
                )
            material.stock_actual = nuevo_stock
        elif tipo_movimiento == 'AJUSTE':
            material.stock_actual = cantidad
        else:
            raise ValidationError(f'Tipo de movimiento inválido: {tipo_movimiento}')
        
        material.save(update_fields=['stock_actual', 'actualizado_en'])
        return material
    
    @staticmethod
    def obtener_materiales_stock_bajo(tipo_inventario: str = None) -> list:
        """
        Obtiene materiales con stock bajo.
        
        Args:
            tipo_inventario: Opcional, filtrar por tipo (CONSTRUCCION o GRANJA)
            
        Returns:
            list: Lista de materiales con stock bajo
        """
        queryset = Material.objects.filter(
            eliminado=False,
            stock_actual__lte=F('stock_minimo_alerta')
        )
        
        if tipo_inventario:
            queryset = queryset.filter(tipo_inventario=tipo_inventario)
        
        return list(queryset)
    
    @staticmethod
    def calcular_valor_inventario(tipo_inventario: str = None) -> Decimal:
        """
        Calcula el valor total del inventario (requiere precio en Material).
        
        Args:
            tipo_inventario: Opcional, filtrar por tipo
            
        Returns:
            Decimal: Valor total del inventario
        """
        # Nota: Esto requiere agregar campo 'precio_unitario' a Material
        # Por ahora retorna 0
        return Decimal('0.00')
