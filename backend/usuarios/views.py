from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permisos import roles_permitidos

from .models import Usuario
from .serializers import UsuarioSerializer

# toda la gestión de usuarios es solo para el administrador (lectura y escritura)
SoloAdministrador = roles_permitidos("ADMINISTRADOR", solo_escritura=False)


class UsuarioListaView(generics.ListCreateAPIView):
    """GET /api/usuarios/  (lista, con ?buscar= ?rol= ?activo=)   y   POST /api/usuarios/  (crear)"""
    serializer_class = UsuarioSerializer
    permission_classes = [SoloAdministrador]

    def get_queryset(self):
        usuarios = Usuario.objects.all().order_by("first_name", "email")
        buscar = self.request.query_params.get("buscar")
        rol = self.request.query_params.get("rol")
        activo = self.request.query_params.get("activo")
        if buscar:
            usuarios = usuarios.filter(Q(email__icontains=buscar) | Q(first_name__icontains=buscar))
        if rol:
            usuarios = usuarios.filter(rol=rol)
        if activo in ("true", "false"):
            usuarios = usuarios.filter(is_active=(activo == "true"))
        return usuarios


class UsuarioDetalleView(generics.RetrieveUpdateDestroyAPIView):
    """GET, PUT/PATCH y DELETE en /api/usuarios/<id>/   (DELETE solo desactiva, no borra)"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [SoloAdministrador]

    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        if usuario == request.user:
            return Response({"detail": "No puedes desactivar tu propio usuario."}, status=400)
        usuario.is_active = False
        usuario.save(update_fields=["is_active"])
        return Response({"detail": "Usuario desactivado."})


class DesbloquearView(APIView):
    """POST /api/usuarios/<id>/desbloquear/"""
    permission_classes = [SoloAdministrador]

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.reiniciar_intentos()
        return Response({"detail": "Usuario desbloqueado."})


class RolesView(APIView):
    """GET /api/usuarios/roles/   (para llenar la lista desplegable en Angular)"""
    permission_classes = [SoloAdministrador]

    def get(self, request):
        return Response([{"valor": valor, "texto": texto} for valor, texto in Usuario.Rol.choices])
