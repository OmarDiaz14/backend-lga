import requests
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import portadaSerializer, PortadaQuerySerializer
from .models import portada

class PortadaViewSet(viewsets.ModelViewSet):
    lookup_value_regex = r'[^/]+'
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
        
    @action(detail=True, methods=['GET'], url_path='get-alfresco-document')
    def get_alfresco_document(self, request, pk=None):
        # Obtiene la instancia de portada
        portada_instance = self.get_object()

        # Verifica si hay un documento asociado
        if not portada_instance.documento_id:
            return Response(
                {"error": "No hay Documento ID asociado a este expediente"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Construye la URL para la consulta
        documento_id = portada_instance.documento_id
        url = f"http://169.47.93.83:8082/api/documents/visualizar/{documento_id}"

        # Realiza la solicitud GET a Alfresco
        response = requests.get(url, stream=True)

        # Verifica el estado de la respuesta
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            file_name = f"{documento_id}.pdf"

            # Devuelve el archivo como respuesta
            return HttpResponse(
                response.content,
                content_type=content_type,
                headers={
                    'Content-Disposition': f'inline; filename="{file_name}"'
                }
            )

        # Maneja errores de la API de Alfresco
        return Response(
            {"error": f"Error al obtener el documento de Alfresco: {response.text}"},
            status=response.status_code
        )
    
    @action(detail=True, methods=['DELETE'], url_path='delete-alfresco-document')
    def delete_alfresco_document(self,request,pk=None):
        portada_instance = self.get_object()

        if not portada_instance.documento_id:
            return Response(
                {"error":"No hay Documento ID asociado a este expediente"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        base_url = "http://169.47.93.83:8082/api/documents/eliminar/"
        documento_id = portada_instance.documento_id
        url = f"{base_url}{documento_id}"

        response = requests.delete(url)

        if response.status_code == 200:
            #limpia todos los campos 
            portada_instance.documento_id = None
            portada_instance.documento_ruta = None
            portada_instance.alfresco_response = None
            portada_instance.save()

            return Response({"message": "Documento eliminado"})
        
        return Response (
            {"error":f"Error al eliminar el documento de Alfresco: {response.text}"},
            status=response.status_code
        )

    @action(detail=True, methods=['GET'], url_path='get-portada-seccion')
    def get_portada_seccion(self, request, pk=None):
        seccion = pk
        try: 
            portadas = portada.obtener_portada_seccion(seccion)
            serializer = PortadaQuerySerializer(portadas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
     
         
    @action(detail=True, methods=['GET'], url_path='get-portada-expediente')
    def get_portada_expediente(self, request, pk=None):
        num_exp = pk
        try: 
            portadas = portada.obtener_expediente(num_exp)
            serializer = PortadaQuerySerializer(portadas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )  
            
    @action(detail=True, methods=['GET'], url_path='get-portada-asunto')
    def get_portada_asunto(self, request, pk=None):
        asunto = pk
        try: 
            portadas = portada.obtener_portada_asunto(asunto)
            serializer = PortadaQuerySerializer(portadas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
