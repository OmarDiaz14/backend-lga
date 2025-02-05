from django.shortcuts import render
from rest_framework import viewsets, permissions
from .serializers import FichaTecSerializer
from .models import FichaTecnica
from rest_framework.permissions import IsAuthenticated


# Create your views here.

class FichaTecViewSet(viewsets.ModelViewSet):
    lookup_value_regex = r'[^/]+'  # Para aceptar valores con / en el campo de búsqueda 
    queryset = FichaTecnica.objects.all()
    permission_classes = []
    serializer_class = FichaTecSerializer


