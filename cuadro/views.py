#from django.shortcuts import render
import pandas as pd
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, permissions
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
class ImportExcelView(viewsets.ModelViewSet):
    queryset = Seccion.objects.none()
    permission_classes = [IsAuthenticated]
    serializer_class = ExcelUploadSerializer

    def validate_columns(self, df, required_columns):
        df.columns = df.columns.str.strip().str.lower()
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f'Columnas faltantes: {", ".join(missing_columns)}')
        return df

    def process_row(self, row):
        # Create or update Seccion
        seccion = Seccion.objects.update_or_create(
            seccion=str(row['seccion']).strip(),
            defaults={
                'codigo_seccion': str(row['codigo_seccion']).strip(),
                'descripcion': str(row['descripcion_seccion']).strip(),
                'delete': False
            }
        )[0]

        # Create or update Series
        serie = Series.objects.update_or_create(
            serie=str(row['serie']).strip(),
            defaults={
                'codigo_serie': str(row['codigo_serie']).strip(),
                'descripcion': str(row['descripcion_serie']).strip(),
                'id_seccion': seccion,
                'delete': False
            }
        )[0]

        # Create or update SubSerie if data exists
        if all(key in row for key in ['subserie', 'codigo_subserie', 'descripcion_subserie']):
            if pd.notna(row['subserie']) and pd.notna(row['descripcion_subserie']):
                SubSerie.objects.update_or_create(
                    subserie=str(row['subserie']).strip(),
                    defaults={
                        'codigo_subserie': str(row['codigo_subserie']).strip(),
                        'descripcion': str(row['descripcion_subserie']).strip(),
                        'id_serie': serie,
                        'delete': False
                    }
                )

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def import_excel(self, request):
        try:
            if 'file' not in request.FILES:
                logger.error("No file provided in request")
                return Response(
                    {'error': 'No se proporcionó archivo'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            required_columns = [
                'seccion', 'codigo_seccion', 'descripcion_seccion',
                'serie', 'codigo_serie', 'descripcion_serie'
            ]

            file = request.FILES['file']
            logger.info(f"Processing file: {file.name}")

            try:
                df = pd.read_excel(file, header=3)
                logger.info(f"Columns found: {df.columns.tolist()}")
            except Exception as e:
                logger.error(f"Excel reading error: {str(e)}")
                return Response(
                    {'error': f'Error al leer el archivo Excel: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                df = self.validate_columns(df, required_columns)
            except ValueError as e:
                logger.error(f"Column validation error: {str(e)}")
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Remove completely empty rows
            df = df.dropna(how='all')

            errors = []
            successful_rows = 0

            for index, row in df.iterrows():
                try:
                    # Skip rows where essential fields are missing
                    if pd.isna(row['seccion']) or pd.isna(row['serie']):
                        errors.append(f'Fila {index + 2}: Campos obligatorios faltantes')
                        continue

                    self.process_row(row)
                    successful_rows += 1

                except Exception as e:
                    logger.error(f"Error processing row {index + 2}: {str(e)}")
                    errors.append(f'Error en fila {index + 2}: {str(e)}')

            response_data = {
                'message': f'Importación completada. {successful_rows} filas procesadas exitosamente.'
            }
            
            if errors:
                response_data['errors'] = errors
                return Response(
                    response_data, 
                    status=status.HTTP_207_MULTI_STATUS
                )

            return Response(
                response_data, 
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"General error during import: {str(e)}")
            return Response(
                {'error': f'Error durante la importación: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
