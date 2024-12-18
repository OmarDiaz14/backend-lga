import requests
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import portadaSerializer
from .models import portada

class PortadaViewSet(viewsets.ModelViewSet):
    queryset = portada.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = portadaSerializer

    @action(detail=False, methods=['POST'], url_path='upload-alfresco-document')
    def upload_alfresco_document(self, request):
        anio = request.data.get('anio')
        expediente = request.data.get('expediente')
        archivo = request.FILES.get('file')

        if not all([anio, expediente, archivo]):
            return Response({
                'error': 'Debe proporcionar año, expediente y archivo'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            portada_instance = portada.objects.get(num_expediente=expediente)
        except portada.DoesNotExist:
            return Response({
                'error': 'No se encontró el expediente especificado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        alfresco_url = 'http://169.47.93.83:8082/api/documents/guardar'

        try:
            files = {
                'file': (
                    archivo.name,
                    archivo.read(),
                    archivo.content_type
                )
            }
            
            data = {
                'anio': anio,
                'expediente': expediente
            }

            respuesta_alfresco = requests.post(
                alfresco_url,
                files=files,
                data=data,
                timeout=30
            )

            if respuesta_alfresco.status_code == 200:
                json_alfresco = {
                    'Mensaje': 'Documento guardado correctamente.',
                    'Ruta': respuesta_alfresco.json().get('Ruta', ''),
                    'DocumentId': respuesta_alfresco.json().get('DocumentId', '')
                }

                portada_instance.actualizar_alfresco(json_alfresco)

                serializer = self.get_serializer(portada_instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else: 
                return Response({
                    'error': 'Error al subir documento a Alfresco', 
                    'detalles': respuesta_alfresco.text,
                    'status_code': respuesta_alfresco.status_code
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except requests.RequestException as e:
            return Response({
                'error': 'Error de conexión al servicio Alfresco',
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'error': 'Error inesperado',
                'detalles': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)