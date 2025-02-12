#from django.shortcuts import render

from rest_framework import viewsets, permissions
from .serializers import  GuiaSerializer
from .models import GuiaDocu
from rest_framework.permissions import IsAuthenticated


# Create your views here.

class GuiaViewSet(viewsets.ModelViewSet):
    queryset = GuiaDocu.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GuiaSerializer