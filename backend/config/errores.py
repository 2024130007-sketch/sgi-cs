"""Mensajes de error en español (RNF-17)."""
from rest_framework.views import exception_handler
def manejador_errores(exc, context):
    respuesta = exception_handler(exc, context)
    if respuesta is not None and isinstance(respuesta.data, dict) and "detail" in respuesta.data:
        respuesta.data = {"detail": str(respuesta.data["detail"])}
    return respuesta