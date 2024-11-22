from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import pdfplumber

from .models import Documento
from .serializers import DocumentoSerializer
# Create your views here.

class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer
    permission_classes = []
    parser_classes = [MultiPartParser]



    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def upload_pdf(self, request, *args, **kwargs):
        #checa si es un pdf 
        file_obj = request.FILES.get('file', None)
        if file_obj is None:
            return Response({"error": "No hay archivo."}, status=status.HTTP_400_BAD_REQUEST)
        
        #procesa el pdf
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                text = page.extract_text()


                #procesa cada linea o seccion (aqui de puede adaptar para cualquier tipo de docmento)
                for line in text.splitlines():
                    #aqui es donde hace la extracion 
                    seccion = "extrae seccion aqui"
                    codigo = "extrae codigo aqui"
                    serie_documental = "extrae serie documental aqui"
                    contenido = line



                    #guarda cada la info en el modelo
                    Documento.objects.create(
                        seccion = seccion,
                        codigo = codigo,
                        serie_documental = serie_documental,
                        contenido = contenido
                    )

        
        return Response ({"message": "PDF procesado y Guardado bien"}, status=status.HTTP_201_CREATED)
    
        




