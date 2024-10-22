from django.shortcuts import render
from rest_framework import viewsets, permissions
from .serializers import FichaTecSerializer
from .models import FichaTecnica
from rest_framework.permissions import IsAuthenticated


# Create your views here.

class FichaTecViewSet(viewsets.ModelViewSet):
    queryset = FichaTecnica.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FichaTecSerializer


