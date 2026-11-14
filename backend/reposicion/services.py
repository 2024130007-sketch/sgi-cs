"""Servicio de alertas (ServicioAlertas del Hito 1)."""
from datetime import date, timedelta
from django.db.models import Sum
from inventario.models import Existencia
from .models import Alerta, ReglaReposicion

UMBRALES_VENCIMIENTO = (30, 60, 90)  # RF-43

def stock_disponible(producto, almacen):
    agg = Existencia.objects.filter(lote__producto=producto, almacen=almacen).aggregate(
        c=Sum("cantidad"), r=Sum("reservada"))
    return (agg["c"] or 0) - (agg["r"] or 0)

def evaluar_reposicion(producto, almacen):
    """RF-41, RF-42, RF-45: alerta si disponible <= punto de reorden y no hay otra abierta."""
    regla = ReglaReposicion.objects.filter(producto=producto, almacen=almacen).first()
    if not regla:
        return None
    
    disp = stock_disponible(producto, almacen)
    if disp > regla.punto_reorden:
        return None
        
    if Alerta.objects.filter(tipo="REPOSICION", producto=producto, almacen=almacen,
                             estado="ABIERTA").exists():
        return None
        
    sugerida = max(regla.stock_maximo - disp, 0)
    return Alerta.objects.create(
        tipo="REPOSICION", producto=producto, almacen=almacen, cantidad_sugerida=sugerida,
        mensaje=f"Stock {disp} <= punto de reorden {regla.punto_reorden} en {almacen.nombre}."
    )

def generar_alertas():
    """Verificación periódica (CU-14). Devuelve cuántas alertas nuevas se crearon."""
    nuevas = 0
    for regla in ReglaReposicion.objects.select_related("producto", "almacen"):
        if evaluar_reposicion(regla.producto, regla.almacen):
            nuevas += 1
            
    hoy = date.today()
    limite = hoy + timedelta(days=max(UMBRALES_VENCIMIENTO))
    
    for e in Existencia.objects.select_related("lote__producto", "almacen").filter(
            cantidad__gt=0, lote__fecha_vencimiento__isnull=False, lote__fecha_vencimiento__lte=limite):
        if Alerta.objects.filter(tipo="VENCIMIENTO", lote=e.lote, almacen=e.almacen,
                                 estado="ABIERTA").exists():
            continue
            
        dias = (e.lote.fecha_vencimiento - hoy).days
        Alerta.objects.create(
            tipo="VENCIMIENTO", producto=e.lote.producto, almacen=e.almacen, lote=e.lote,
            mensaje=f"Lote {e.lote.numero} vence en {dias} día(s)." if dias >= 0
            else f"Lote {e.lote.numero} VENCIDO hace {-dias} día(s)."
        )
        nuevas += 1
    return nuevas