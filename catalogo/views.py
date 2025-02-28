#from django.shortcuts import render

from rest_framework import viewsets, permissions
from .serializers import  CatalogoSerializer, DestinoSerializer,TypeSerializer,ValoresSerializer, CatalogoSeccionSerializer
from .models import Catalogo, destino_expe, type_access, valores_docu
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class DestinoViewSet(viewsets.ModelViewSet):
    queryset = destino_expe.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = DestinoSerializer

class TypeViewSet(viewsets.ModelViewSet):
    queryset = type_access.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TypeSerializer

class ValorViewSet(viewsets.ModelViewSet):
    queryset = valores_docu.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ValoresSerializer



class CatalogoViewSet(viewsets.ModelViewSet):
    lookup_value_regex = r'[^/]+'
    queryset = Catalogo.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CatalogoSerializer

    @action(detail=True, methods=['GET'], url_path='get-catalogo-seccion')
    def get_catalogo_seccion(self, request, pk=None):
        id_seccion = pk
        try:
            catalogo = Catalogo.obtener_catalogo_seccion(id_seccion)
            serializer = CatalogoSeccionSerializer(catalogo, many=True)
            catalogo = serializer.data
            return Response(catalogo, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )