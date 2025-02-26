from django.shortcuts import render
from rest_framework import viewsets, permissions
from .serializers import FichaTecSerializer, FichaTecSeccionSerializer
from .models import FichaTecnica
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


# Create your views here.

class FichaTecViewSet(viewsets.ModelViewSet):
    lookup_value_regex = r'[^/]+'
    queryset = FichaTecnica.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FichaTecSerializer
    
    @action(detail=True, methods=['GET'], url_path='get-ficha-seccion')
    def get_ficha_seccion(self, request, pk=None):
        id_seccion = pk
        try:
            fichas = FichaTecnica.obtener_ficha_seccion(id_seccion)
            serializer = FichaTecSeccionSerializer(fichas, many=True)
            fichas = serializer.data
            return Response(fichas, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


