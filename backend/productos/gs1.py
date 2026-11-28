"""Lectura de códigos GS1-128 (RF #33).

Un código GS1-128 junta varios datos, cada uno precedido por un identificador
de aplicación (AI):

    01  GTIN del producto (14 dígitos fijos)
    17  fecha de vencimiento AAMMDD (6 fijos)
    10  número de lote (hasta 20, variable)
    21  número de serie (hasta 20, variable)

Los campos de largo variable terminan con el separador FNC1 (carácter 0x1d).
Se aceptan dos formatos de entrada:
    - legible:  (01)07791234567893(17)261231(10)L001
    - crudo:    010779123456789317261231 10L001   (con 0x1d tras un campo variable)
"""
import calendar
import re
from datetime import date

GS = "\x1d"
FIJOS = {"01": 14, "02": 14, "11": 6, "13": 6, "15": 6, "17": 6}
VARIABLES = {"10": 20, "21": 20}


class CodigoInvalido(ValueError):
    """El texto leído no es un GS1-128 válido."""


def gtin_valido(gtin):
    """Dígito de control módulo 10 (sirve para EAN-8, EAN-13, GTIN-14)."""
    if not gtin.isdigit() or len(gtin) not in (8, 12, 13, 14):
        return False
    digitos = [int(c) for c in gtin]
    suma = sum(n * (3 if i % 2 == 0 else 1) for i, n in enumerate(reversed(digitos[:-1])))
    return (10 - suma % 10) % 10 == digitos[-1]


def _fecha(aammdd):
    """AAMMDD -> date. El día 00 significa «último día del mes»."""
    if len(aammdd) != 6 or not aammdd.isdigit():
        raise CodigoInvalido("Fecha de vencimiento inválida")
    anio, mes, dia = 2000 + int(aammdd[:2]), int(aammdd[2:4]), int(aammdd[4:])
    if not 1 <= mes <= 12:
        raise CodigoInvalido("Fecha de vencimiento inválida")
    ultimo = calendar.monthrange(anio, mes)[1]
    if dia == 0:
        dia = ultimo
    if dia > ultimo:
        raise CodigoInvalido("Fecha de vencimiento inválida")
    return date(anio, mes, dia)


def parece_gs1(texto):
    t = texto.strip()
    return t.startswith("(") or t.startswith("]C1") or (t.startswith("01") and len(t) > 16)


def parsear_gs1(texto):
    """Devuelve {'gtin', 'lote', 'serie', 'vencimiento'} (claves ausentes = None)."""
    t = (texto or "").strip().replace("]C1", "")
    if not t:
        raise CodigoInvalido("Código vacío")
    if "(" in t:
        datos = dict(re.findall(r"\((\d{2})\)([^()]*)", t))
    else:
        datos, i = {}, 0
        while i < len(t):
            ai, i = t[i:i + 2], i + 2
            if ai in FIJOS:
                datos[ai], i = t[i:i + FIJOS[ai]], i + FIJOS[ai]
            elif ai in VARIABLES:
                fin = t.find(GS, i)
                fin = len(t) if fin < 0 else fin
                datos[ai], i = t[i:fin][:VARIABLES[ai]], fin + 1
            else:
                raise CodigoInvalido(f"Identificador no soportado: {ai}")
    if not datos:
        raise CodigoInvalido("No se encontraron datos GS1")
    gtin = datos.get("01")
    if gtin is not None and not gtin_valido(gtin):
        raise CodigoInvalido("GTIN con dígito de control inválido")
    vence = datos.get("17")
    return {
        "gtin": gtin,
        "lote": datos.get("10") or None,
        "serie": datos.get("21") or None,
        "vencimiento": _fecha(vence) if vence else None,
    }
