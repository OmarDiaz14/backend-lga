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
            raise ValueError(
                f'Columnas faltantes en la hoja/sección "{sheet_name}": {", ".join(missing_columns)}')
        return df

    def find_start_rows(self, file):
        df = pd.read_excel(file, header=None)
        # Eliminar filas vacías
        df.dropna(how='all', inplace=True)

        section_start = None
        series_start = None
        subseries_start = None

        for index, row in df.iterrows():
            row_lower = [str(item).lower().strip() for item in row.tolist()]  # Normalizacion de los datos leidos
            if section_start is None and 'codigo' in row_lower and 'secciones' in row_lower:
                section_start = index + 1
            elif series_start is None and 'codigo' in row_lower and 'series' in row_lower:
                series_start = index + 1
            elif subseries_start is None and 'codigo' in row_lower and 'subserie' in row_lower:
                subseries_start = index + 1

        if section_start is None or series_start is None:
            raise ValueError("No se encontraron los encabezados de secciones o series en el archivo.")

        return section_start, series_start, subseries_start

    def clean_dataframe(self, df, codigo_col='codigo'):
        """Limpia el DataFrame eliminando filas con valores nan o con cabeceras duplicadas"""
        # Eliminar filas donde el código es nan, None, o cadenas vacías
        df = df.dropna(subset=[codigo_col])
        
        # Filtrar filas donde código contiene valores que parecen encabezados
        df = df[~df[codigo_col].astype(str).str.lower().isin(['codigo', 'nan', 'none', ''])]
        
        # Eliminar filas donde todos los valores son iguales a sus nombres de columna
        mask = df.apply(lambda row: not all(str(val).lower() == col.lower() 
                                         for col, val in row.items() 
                                         if pd.notna(val) and str(val).strip() != ''), axis=1)
        df = df[mask]
        
        return df

    def process_sections(self, df):
        # Limpiar el DataFrame antes de procesarlo
        df = self.clean_dataframe(df)
        
        sections_dict = {}
        for index, row in df.iterrows():
            try:
                codigo = str(row['codigo']).strip()
                seccion = str(row['secciones']).strip()
                
                # Verificar que el código no tenga puntos (no es una subsección)
                if '.' not in codigo:
                    # Guardamos el código tal como está en el Excel
                    seccion_obj, created = Seccion.objects.update_or_create(
                        codigo_seccion=codigo,
                        defaults={'seccion': seccion, 'descripcion': seccion, 'delete': False}
                    )
                    sections_dict[codigo] = seccion_obj
                    logger.info(f"Sección procesada: {codigo}")
                else:
                    logger.warning(f"Código {codigo} contiene puntos y no fue procesado como sección")
            except Exception as e:
                logger.error(f"Error procesando sección en fila {index + 2}: {str(e)}")
                raise ValueError(f'Error en fila {index + 2}: {str(e)}')
        return sections_dict

    def process_series(self, df, sections_dict):
        # Limpiar el DataFrame antes de procesarlo
        df = self.clean_dataframe(df)
        
        series_dict = {}
        for index, row in df.iterrows():
            try:
                codigo = str(row['codigo']).strip()
                # Verificar si codigo es una cadena antes de dividir
                if isinstance(codigo, str):
                    try:
                        # Obtenemos el código de sección (primera parte del código)
                        parts = codigo.split('.')
                        # Para series, el formato debería ser como "1C.1" donde "1C" es la sección
                        section_code = parts[0]  # Tomamos solo la primera parte como código de sección
                        
                        # Solo procesar si es una serie (tiene formato de código con punto)
                        if '.' in codigo:
                            series = str(row['series']).strip()
                            section = sections_dict.get(section_code)  # Usamos el código de sección
                            
                            if section:
                                serie_obj, created = Series.objects.update_or_create(
                                    codigo_serie=codigo,
                                    defaults={'serie': series, 'descripcion': series, 'id_seccion': section, 'delete': False}
                                )
                                series_dict[codigo] = serie_obj
                                logger.info(f"Serie procesada: {codigo}")
                            else:
                                logger.warning(f"No se encontró la sección con código: {section_code} para la serie: {codigo}")
                        else:
                            logger.info(f"Código {codigo} no tiene formato de serie, se omitió")
                    except IndexError:
                        logger.error(f"Error procesando serie en fila {index + 2}: Formato de código inválido: {codigo}")
                        raise ValueError(f'Error en fila {index + 2}: Formato de código inválido: {codigo}')
                else:
                    logger.error(f"Error procesando serie en fila {index + 2}: Código no es una cadena: {codigo}")
                    raise ValueError(f'Error en fila {index + 2}: Código no es una cadena: {codigo}')
            except Exception as e:
                logger.error(f"Error procesando serie en fila {index + 2}: {str(e)}")
                raise ValueError(f'Error en fila {index + 2}: {str(e)}')
        return series_dict
    
    def process_subseries(self, df, series_dict):
        # Limpiar el DataFrame antes de procesarlo
        df = self.clean_dataframe(df)
        
        for index, row in df.iterrows():
            try:
                codigo = str(row['codigo']).strip()
                subserie = str(row['subserie']).strip()
                
                # Verificar que sea un código de subserie (debe tener al menos dos puntos)
                parts = codigo.split('.')
                if len(parts) >= 3:  # Debe tener al menos 3 partes para ser subserie
                    serie_code = '.'.join(parts[:-1])  # Todo excepto la última parte
                    
                    serie = series_dict.get(serie_code)
                    if serie:
                        SubSerie.objects.update_or_create(
                            codigo_subserie=codigo,
                            defaults={'subserie': subserie, 'descripcion': subserie, 'id_serie': serie, 'delete': False}
                        )
                        logger.info(f"Subserie procesada: {codigo}")
                    else:
                        logger.warning(f"No se encontró la serie con código: {serie_code} para la subserie: {codigo}")
                else:
                    logger.warning(f"Formato de código inválido para subserie (debe tener al menos dos puntos): {codigo}")
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

            # Guardamos una copia del archivo original antes de procesarlo
            file_copy = file
            section_start, series_start, subseries_start = self.find_start_rows(file)

            # Reiniciamos el puntero del archivo para volver a leerlo
            file_copy.seek(0)
            df_sections = pd.read_excel(file_copy, skiprows=section_start - 1)
            df_sections = self.validate_columns(df_sections, ['codigo', 'secciones'], 'Secciones')
            sections_dict = self.process_sections(df_sections)

            # Reiniciamos el puntero del archivo para leer las series
            file_copy.seek(0)
            df_series = pd.read_excel(file_copy, skiprows=series_start - 1)
            df_series = self.validate_columns(df_series, ['codigo', 'series'], 'Series')
            series_dict = self.process_series(df_series, sections_dict)

            if subseries_start is not None:
                file_copy.seek(0)
                df_subseries = pd.read_excel(file_copy, skiprows=subseries_start - 1)
                df_subseries = self.validate_columns(df_subseries, ['codigo', 'subserie'], 'Subseries')
                self.process_subseries(df_subseries, series_dict)

            return Response({'message': 'Importación completada exitosamente'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return Response({'error': f'Error procesando el archivo: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)