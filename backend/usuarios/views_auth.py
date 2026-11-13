from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import MINUTOS_BLOQUEO, Usuario
from .serializers import datos_de_sesion

MENSAJE_CREDENCIALES = "Correo o contraseña incorrectos."


def respuesta_error(mensaje, codigo):
    return Response({"detail": mensaje}, status=codigo)


def texto_minutos(cantidad):
    return "1 minuto" if cantidad == 1 else f"{cantidad} minutos"


class LoginView(APIView):
    """POST /api/auth/login   con   { "email": "...", "password": "..." }"""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = str(request.data.get("email") or "").strip().lower()
        password = str(request.data.get("password") or "")
        if not email or not password:
            return respuesta_error("Escribe tu correo y tu contraseña.", 400)

        usuario = Usuario.objects.filter(email__iexact=email).first()
        if usuario is None:
            # mismo mensaje que con clave incorrecta, para no revelar qué correos existen
            return respuesta_error(MENSAJE_CREDENCIALES, 401)

        if usuario.esta_bloqueado():
            faltan = texto_minutos(usuario.minutos_restantes())
            return respuesta_error(f"Tu cuenta está bloqueada por intentos fallidos. Intenta de nuevo en {faltan}.", 423)
        if usuario.bloqueado_hasta is not None:
            usuario.reiniciar_intentos()   # el bloqueo ya terminó, se empieza de cero

        if not usuario.check_password(password):
            usuario.registrar_intento_fallido()
            if usuario.esta_bloqueado():
                return respuesta_error(
                    f"Demasiados intentos fallidos. Tu cuenta quedó bloqueada por {texto_minutos(MINUTOS_BLOQUEO)}.", 423)
            return respuesta_error(MENSAJE_CREDENCIALES, 401)

        if not usuario.is_active:
            return respuesta_error("Tu usuario está desactivado. Habla con el administrador.", 403)

        usuario.reiniciar_intentos()
        refresh = RefreshToken.for_user(usuario)
        return Response({
            "access": str(refresh.access_token),   # dura 15 minutos (settings.py), luego la sesión expira
            "refresh": str(refresh),
            "usuario": datos_de_sesion(usuario),
        })


class LogoutView(APIView):
    """POST /api/auth/logout"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Con JWT el servidor no guarda la sesión: el cierre real lo hace Angular
        # borrando su token. Este endpoint solo confirma que la petición fue válida.
        return Response({"detail": "Sesión cerrada."})
