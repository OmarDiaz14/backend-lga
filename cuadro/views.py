#from django.shortcuts import render
import pandas as pd
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.viewsets import GenericViewSet
from .serializers import  SeccionSerializer, SerieSerializer, SubSerieSerializer, ExcelUploadSerializer
from .models import Seccion, Series, SubSerie
from rest_framework.permissions import IsAuthenticated
import logging

# Create your views here.

class SeccionViewSet(viewsets.ModelViewSet):
    queryset = Seccion.objects.all()
    permission_classes = [IsAuthenticated]  
    serializer_class = SeccionSerializer
    

class SerieViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.all()
    permission_classes = [IsAuthenticated]  
    serializer_class = SerieSerializer
    

class SubSerieViewSet(viewsets.ModelViewSet):
    queryset = SubSerie.objects.all()
    permission_classes = [IsAuthenticated]  
    serializer_class = SubSerieSerializer


logger = logging.getLogger(__name__)
class ImportExcelView(GenericViewSet):
    serializer_class = ExcelUploadSerializer
    permission_classes = []

    def validate_columns(self, df, sheet_number):
        df.columns = df.columns.str.strip().str.lower()
        
        if sheet_number == 0:  # Primera sección del Excel
            required_columns = ['codigo', 'secciones']
        else:  # Segunda sección del Excel
            required_columns = ['codigo', 'seccion', 'series']
            
        missing_columns = [col for col in required_columns if col.lower() not in df.columns]
        if missing_columns:
            raise ValueError(f'Columnas faltantes en la hoja {sheet_number + 1}: {", ".join(missing_columns)}')
        return df

    def process_sections(self, df):
        sections_dict = {}
        for index, row in df.iterrows():
            try:
                if pd.notna(row['codigo']) and pd.notna(row['secciones']):
                    codigo = str(row['codigo']).strip()
                    if codigo.endswith('C'):
                        seccion = Seccion.objects.update_or_create(
                            codigo_seccion=codigo,
                            defaults={
                                'seccion': str(row['secciones']).strip(),
                                'descripcion': str(row['secciones']).strip(),
                                'delete': False
                            }
                        )[0]
                        sections_dict[codigo.replace('C', '')] = seccion
                        logger.info(f"Sección procesada: {codigo}")
            except Exception as e:
                logger.error(f"Error procesando sección en fila {index + 2}: {str(e)}")
                raise ValueError(f'Error en fila {index + 2}: {str(e)}')
        return sections_dict

    def process_series(self, df, sections_dict):
        series_dict = {}
        for index, row in df.iterrows():
            try:
                if pd.notna(row.get('codigo', '')) and pd.notna(row.get('series', '')):
                    codigo = str(row['codigo']).strip()
                    series = str(row['series']).strip()
                    
                    # Extraer el código de sección (1C de 1C.1)
                    section_code = codigo.split('.')[0] + 'C'
                    
                    # Buscar la sección correspondiente
                    section = sections_dict.get(section_code.replace('C', ''))
                    
                    if section:
                        serie = Series.objects.update_or_create(
                            codigo_serie=codigo,
                            defaults={
                                'serie': series,
                                'descripcion': series,
                                'id_seccion': section,
                                'delete': False
                            }
                        )[0]
                        series_dict[codigo] = serie
                        logger.info(f"Serie procesada: {codigo}")
            except Exception as e:
                logger.error(f"Error procesando serie en fila {index + 2}: {str(e)}")
                raise ValueError(f'Error en fila {index + 2}: {str(e)}')

    @action(detail=False, methods=['post'], url_path='upload')
    @transaction.atomic
    def import_excel(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            file = serializer.validated_data['file']
            logger.info(f"Procesando archivo: {file.name}")

            try:
                # Leer las secciones (primera parte del Excel)
                df_sections = pd.read_excel(file, nrows=12, skiprows=3)  # Skip 3 rows to start from actual data
                df_sections = self.validate_columns(df_sections, 0)
                
                if df_sections.empty:
                    raise ValueError('No se encontraron secciones en el archivo')

                # Leer las series (segunda parte del Excel)
                df_series = pd.read_excel(file, skiprows=18)  # Skip 18 rows to start from series data
                df_series = self.validate_columns(df_series, 1)
                
                if df_series.empty:
                    raise ValueError('No se encontraron series en el archivo')

                with transaction.atomic():
                    sections_dict = self.process_sections(df_sections)
                    self.process_series(df_series, sections_dict)

                return Response(
                    {'message': 'Importación completada exitosamente'},
                    status=status.HTTP_201_CREATED
                )

            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f"Error inesperado: {str(e)}")
                return Response(
                    {'error': f'Error procesando el archivo: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Error en la importación: {str(e)}")
            return Response(
                {'error': f'Error durante la importación: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )