from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import ColaERP, EquivalenciaERP

MAX_INTENTOS = 5

class ErrorERP(Exception):
    pass

def encolar(tipo, payload):
    """Agrega un evento a la cola para ser enviado al ERP."""
    return ColaERP.objects.create(tipo=tipo, payload=payload)

def traducir(payload):
    """#30: Traduce los SKUs del sistema a los códigos del ERP."""
    lineas = []
    for l in payload.get("lineas", []):
        eq = EquivalenciaERP.objects.filter(producto__sku=l["sku"]).first()
        if not eq:
            raise ErrorERP(f"Sin equivalencia ERP para el SKU {l['sku']}")
        lineas.append({**l, "codigo_erp": eq.codigo_erp, "unidad": eq.unidad_erp})
    return {**payload, "lineas": lineas}

def enviar_al_erp(datos):
    """Cliente ERP simulado. Se puede tumbar para probar los reintentos."""
    if getattr(settings, "ERP_SIMULAR_CAIDA", False):
        raise ErrorERP("ERP no disponible (simulado)")
    return {"ok": True}

def procesar_pendientes():
    """Toma los pendientes y los envía. Reintenta con espera creciente."""
    ahora = timezone.now()
    # Tomamos los pendientes cuyo tiempo de reintento ya pasó
    pendientes = ColaERP.objects.filter(estado="PENDIENTE", proximo_intento__lte=ahora)
    
    for item in pendientes:
        try:
            enviar_al_erp(traducir(item.payload))
            item.estado = "ENVIADO"
        except ErrorERP as e:
            item.intentos += 1
            item.ultimo_error = str(e)[:300]
            if item.intentos >= MAX_INTENTOS:
                item.estado = "ERROR"
            else:
                # Espera 2, 4, 8... minutos
                item.proximo_intento = ahora + timedelta(minutes=2 ** item.intentos)
        item.save()