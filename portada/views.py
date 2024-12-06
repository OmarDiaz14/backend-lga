from django.shortcuts import render
from rest_framework import viewsets, permissions
from .serializers import portadaSerializer
from .models import portada
from rest_framework.permissions import IsAuthenticated

# Create your views here.



class PortadaViewSet (viewsets.ModelViewSet):
    queryset = portada.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = portadaSerializer
