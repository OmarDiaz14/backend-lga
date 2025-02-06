import requests
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import dashboard
from .serializers import DashboardSerializer

class DashboardViewSet(viewsets.ModelViewSet):
    lookup_value_regex = r'[^/]+'
    queryset = dashboard.objects.all()
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['GET'], url_path='get-dashboard')
    def get_dashboard(self, request, pk=None):
        id_seccion = pk
        try:
            series = dashboard.obtener_total_series(id_seccion)
            serializer = DashboardSerializer(series, many=True)
            total_expedientes_data = dashboard.obtener_total_expedientes(id_seccion)
            total_expedientes = total_expedientes_data.get("total_expedientes", 0)
            
            response_data = {
                "series": serializer.data,
                "total_expedientes": total_expedientes
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )