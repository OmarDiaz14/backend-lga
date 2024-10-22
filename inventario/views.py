from django.shortcuts import render
from rest_framework import viewsets, permissions
from .serializers import InventarioSerializer
from .models import Inventario
from rest_framework.permissions import IsAuthenticated

# Create your views here.



class InventarioViewSet (viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = InventarioSerializer
