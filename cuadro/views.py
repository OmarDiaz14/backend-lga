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

    def validate_columns(self, df, required_columns, sheet_name):
        df.columns = df.columns.str.strip().str.lower()
        missing_columns = [col for col in required_columns if col.lower() not in df.columns]
        if missing_columns:
            raise ValueError(f'Columnas faltantes en la hoja/sección "{sheet_name}": {", ".join(missing_columns)}')
        return df

    def find_start_rows(self, file):
        df = pd.read_excel(file, header=None)
        section_start = None
        series_start = None
        subseries_start = None

        for index, row in df.iterrows():
            row_lower = [str(item).lower().strip() for item in row.tolist()] # Normalizacion de los datos leidos
            if section_start is None and 'codigo' in row_lower and 'secciones' in row_lower:
                section_start = index + 1
            elif series_start is None and 'codigo' in row_lower and 'series' in row_lower:
                series_start = index + 1
            elif subseries_start is None and 'codigo' in row_lower and 'subserie' in row_lower:
                subseries_start = index + 1

        if section_start is None or series_start is None:
            raise ValueError("No se encontraron los encabezados de secciones o series en el archivo.")

        return section_start, series_start, subseries_start

    def process_sections(self, df):
        """
        Procesa las secciones del DataFrame y las guarda en la base de datos.
        Maneja códigos que terminan en 'C' o 'S'.
        """
        sections_dict = {}
        for index, row in df.iterrows():
            try:
                codigo = str(row['codigo']).strip()
                seccion = str(row['secciones']).strip()
                if codigo.endswith(('C', 'S')):  # Verifica si termina en 'C' o 'S'
                    seccion_obj, _ = Seccion.objects.update_or_create(
                        codigo_seccion=codigo,
                        defaults={'seccion': seccion, 'descripcion': seccion, 'delete': False}
                    )
                    sections_dict[codigo.rstrip('CS')] = seccion_obj  # Elimina 'C' o 'S' al final
                    logger.info(f"Sección procesada: {codigo}")
            except Exception as e:
                logger.error(f"Error procesando sección en fila {index + 2}: {str(e)}")
                raise ValueError(f'Error en fila {index + 2}: {str(e)}')
        return sections_dict

    def process_series(self, df, sections_dict):
        """
        Procesa las series del DataFrame y las guarda en la base de datos.
        Maneja códigos de sección que terminan en 'C' o 'S'.
        """
        series_dict = {}
        for index, row in df.iterrows():
            try:
                codigo = str(row['codigo']).strip()
                series = str(row['series']).strip()
                section_code_list = codigo.split('.')  # Obtiene el código de sección como lista
                section_code = '.'.join(section_code_list)  # Convierte la lista en una cadena
                # Busca la sección en el diccionario, probando con 'C' y 'S' al final
                section = sections_dict.get(section_code + 'C') or sections_dict.get(section_code + 'S')
                if section:
                    serie_obj, _ = Series.objects.update_or_create(
                        codigo_serie=codigo,
                        defaults={'serie': series, 'descripcion': series, 'id_seccion': section, 'delete': False}
                    )
                    series_dict[codigo] = serie_obj
                    logger.info(f"Serie procesada: {codigo}")
            except Exception as e:
                logger.error(f"Error procesando serie en fila {index + 2}: {str(e)}")
                raise ValueError(f'Error en fila {index + 2}: {str(e)}')
        return series_dict


    def process_subseries(self, df, series_dict):
        for index, row in df.iterrows():
            try:
                codigo = str(row['codigo']).strip()
                subserie = str(row['subserie']).strip()
                serie = series_dict.get(codigo.split('.')[0] + '.' + codigo.split('.')[1])
                if serie:
                    SubSerie.objects.update_or_create(
                        codigo_subserie=codigo,
                        defaults={'subserie': subserie, 'descripcion': subserie, 'id_serie': serie, 'delete': False}
                    )
                    logger.info(f"Subserie procesada: {codigo}")
            except Exception as e:
                logger.error(f"Error procesando subserie en fila {index + 2}: {str(e)}")
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

            # Imprime el DataFrame leido del excel para Debugging
            df_debug = pd.read_excel(file, header=None)
            print(df_debug)

            section_start, series_start, subseries_start = self.find_start_rows(file)

            df_sections = pd.read_excel(file, skiprows=section_start - 1)
            df_sections = self.validate_columns(df_sections, ['codigo', 'secciones'], 'Secciones')
            sections_dict = self.process_sections(df_sections)

            df_series = pd.read_excel(file, skiprows=series_start - 1)
            df_series = self.validate_columns(df_series, ['codigo', 'series'], 'Series')
            series_dict = self.process_series(df_series, sections_dict)

            if subseries_start is not None:
                df_subseries = pd.read_excel(file, skiprows=subseries_start-1)
                df_subseries = self.validate_columns(df_subseries, ['codigo', 'subserie'], 'Subseries')
                self.process_subseries(df_subseries, series_dict)

            return Response({'message': 'Importación completada exitosamente'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return Response({'error': f'Error procesando el archivo: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)