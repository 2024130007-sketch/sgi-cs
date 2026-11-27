from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permisos import roles_permitidos
from usuarios.models import Usuario
from .models import RegistroRespaldo
from .serializers import RegistroRespaldoSerializer
from .services.backup import crear_respaldo


class RespaldoListCreateView(APIView):
    permission_classes = [
        roles_permitidos(
            Usuario.Rol.ADMINISTRADOR,
            solo_escritura=False,
        )
    ]

    def get(self, request):
        registros = RegistroRespaldo.objects.select_related("usuario").all()
        serializer = RegistroRespaldoSerializer(registros, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            registro = crear_respaldo(usuario=request.user)
        except Exception as exc:
            return Response(
                {"detail": f"No se pudo generar el respaldo: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = RegistroRespaldoSerializer(registro)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
