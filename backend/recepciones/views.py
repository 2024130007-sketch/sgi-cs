from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Recepcion
from .serializers import RecepcionSerializer
from . import services

class RecepcionViewSet(viewsets.ModelViewSet):
    queryset = Recepcion.objects.all()
    serializer_class = RecepcionSerializer

    def create(self, request, *args, **kwargs):
        return Response({"detail": "Endpoint de recepción en construcción"}, status=status.HTTP_201_CREATED)