import logging
import pandas as pd
from django.db import transaction
from rest_framework import status, viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import time

from .serializers import (
    SeccionSerializer, 
    SerieSerializer, 
    SubSerieSerializer, 
    ExcelUploadSerializer, 
    SerieSeccionSerializer, 
    SubseriesSeccionSerializer
)
from .models import Seccion, Series, SubSerie

# Configuración del logger
logger = logging.getLogger(__name__)

# Configuración de chunks para procesar datos por lotes
CHUNK_SIZE = getattr(settings, 'EXCEL_IMPORT_CHUNK_SIZE', 100)


class BaseViewSet(viewsets.ModelViewSet):
    """ViewSet base para operaciones CRUD con configuraciones comunes."""
    permission_classes = []
    lookup_value_regex = r'[^/]+'


class SeccionViewSet(BaseViewSet):
    """ViewSet para operaciones CRUD en el modelo Seccion."""
    queryset = Seccion.objects.all()
    serializer_class = SeccionSerializer


class SerieViewSet(BaseViewSet):
    """ViewSet para operaciones CRUD en el modelo Series."""
    queryset = Series.objects.all()
    serializer_class = SerieSerializer
    
    @action(detail=True, methods=['GET'], url_path='get-series-seccion')
    def get_series_seccion(self, request, pk=None):
        """Obtiene todas las series asociadas a una sección específica."""
        try:
            series = Series.obtener_series_seccion(pk)
            series_data = SerieSeccionSerializer(series, many=True).data
            return Response(series_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error obteniendo series para la sección {pk}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubSerieViewSet(BaseViewSet):
    """ViewSet para operaciones CRUD en el modelo SubSerie."""
    queryset = SubSerie.objects.all()
    serializer_class = SubSerieSerializer
    
    @action(detail=True, methods=['GET'], url_path='get-subseries-seccion')
    def get_subseries_seccion(self, request, pk=None):
        """Obtiene todas las subseries asociadas a una sección específica."""
        try:
            subseries = SubSerie.obtener_subseries_seccion(pk)
            subseries_data = SubseriesSeccionSerializer(subseries, many=True).data
            return Response(subseries_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error obteniendo subseries para la sección {pk}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExcelProcessor:
    """Clase base para procesamiento de archivos Excel."""
    
    @staticmethod
    def validate_columns(df, required_columns, sheet_name):
        """Valida que el DataFrame contenga las columnas requeridas."""
        df.columns = df.columns.str.strip().str.lower()
        missing_columns = [col for col in required_columns if col.lower() not in df.columns]
        if missing_columns:
            raise ValueError(
                f'Columnas faltantes en la hoja "{sheet_name}": {", ".join(missing_columns)}')
        return df
    
    @staticmethod
    def find_section_headers(file):
        """Encuentra los encabezados de sección en el archivo Excel de manera optimizada."""
        try:
            # Leer solo las primeras 30 filas para buscar encabezados (optimización)
            df = pd.read_excel(file, header=None, nrows=30)
            df.dropna(how='all', inplace=True)

            section_markers = {
                'section': ('codigo', 'secciones'),
                'series': ('codigo', 'series'),
                'subseries': ('codigo', 'subserie')
            }
            
            start_rows = {k: None for k in section_markers.keys()}
            
            for index, row in df.iterrows():
                row_lower = [str(item).lower().strip() for item in row.tolist() if pd.notna(item)]
                for section, markers in section_markers.items():
                    if start_rows[section] is None and all(marker in row_lower for marker in markers):
                        start_rows[section] = index + 1
            
            if start_rows['section'] is None or start_rows['series'] is None:
                raise ValueError("No se encontraron los encabezados de secciones o series en el archivo.")
                
            return start_rows['section'], start_rows['series'], start_rows['subseries']
        except Exception as e:
            logger.error(f"Error buscando encabezados de sección: {str(e)}")
            raise
    
    @staticmethod
    def clean_dataframe(df, codigo_col='codigo'):
        """Limpia el DataFrame eliminando filas con valores nan o con cabeceras duplicadas."""
        # Optimización: usar .loc para operaciones más eficientes
        if df.empty:
            return df
            
        # Eliminar filas donde el código es nan, None, o cadenas vacías
        df = df.dropna(subset=[codigo_col])
        
        # Filtrar rows donde código contiene valores que parecen encabezados (más eficiente)
        invalid_codes = ['codigo', 'nan', 'none', '']
        mask = ~df[codigo_col].astype(str).str.lower().isin(invalid_codes)
        df = df.loc[mask]
        
        return df
    
    @staticmethod
    def read_excel_in_chunks(file, skiprows, usecols=None):
        """Lee el archivo Excel por completo, pero procesa los datos en chunks manualmente."""
        # Leer el archivo completo primero
        df = pd.read_excel(
            file, 
            skiprows=skiprows, 
            usecols=usecols
        )
        
        # Si está vacío, retornar un DataFrame vacío
        if df.empty:
            return pd.DataFrame()
        
        # Si se necesita procesar en chunks para evitar problemas de memoria,
        # se puede dividir el DataFrame después de leerlo
        chunks = []
        for i in range(0, len(df), CHUNK_SIZE):
            chunk = df.iloc[i:i+CHUNK_SIZE]
            chunks.append(chunk)
        
        if chunks:
            return pd.concat(chunks) if len(chunks) > 1 else chunks[0]
        return pd.DataFrame()


class BatchProcessor:
    """Clase para procesar datos en lotes para optimizar el uso de memoria."""
    
    @staticmethod
    def process_in_batches(df, process_func, batch_size=100, **kwargs):
        """Procesa un DataFrame en lotes para evitar problemas de memoria."""
        if df.empty:
            return {} if 'dict' in process_func.__name__ else None
            
        results = {}
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        for i in range(total_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(df))
            batch = df.iloc[start_idx:end_idx]
            
            batch_result = process_func(batch, **kwargs)
            if isinstance(batch_result, dict):
                results.update(batch_result)
                
            # Evitar timeouts dando oportunidad al sistema de procesar otras tareas
            if i % 10 == 0 and i > 0:
                time.sleep(0.1)  # Pequeña pausa para evitar bloquear el hilo
                
        return results


class SectionProcessor:
    """Clase para procesar secciones de un archivo Excel."""
    
    @staticmethod
    def process_batch(df, existing_sections=None):
        """Procesa un lote de secciones desde el DataFrame."""
        df = ExcelProcessor.clean_dataframe(df)
        
        sections_dict = {}
        objects_to_create = []
        objects_to_update = {}
        
        # Preparar los objetos para creación masiva
        for _, row in df.iterrows():
            try:
                codigo = str(row['codigo']).strip()
                seccion = str(row['secciones']).strip()
                
                # Verificar que el código no tenga puntos (no es una subsección)
                if '.' not in codigo:
                    if existing_sections and codigo in existing_sections:
                        objects_to_update[codigo] = {
                            'seccion': seccion, 
                            'descripcion': seccion, 
                            'delete': False
                        }
                    else:
                        objects_to_create.append(
                            Seccion(
                                codigo_seccion=codigo,
                                seccion=seccion,
                                descripcion=seccion,
                                delete=False
                            )
                        )
            except Exception as e:
                logger.warning(f"Error procesando sección: {str(e)}")
                continue  # Continuar con la siguiente fila
        
        # Crear en masa
        if objects_to_create:
            created_sections = Seccion.objects.bulk_create(objects_to_create)
            for section in created_sections:
                sections_dict[section.codigo_seccion] = section
                
        # Actualizar existentes si es necesario
        if objects_to_update:
            existing = Seccion.objects.filter(codigo_seccion__in=list(objects_to_update.keys()))
            for section in existing:
                updates = objects_to_update[section.codigo_seccion]
                for key, value in updates.items():
                    setattr(section, key, value)
                section.save()
                sections_dict[section.codigo_seccion] = section
        
        return sections_dict


class SeriesProcessor:
    """Clase para procesar series de un archivo Excel."""
    
    @staticmethod
    def process_batch(df, sections_dict):
        """Procesa un lote de series desde el DataFrame."""
        df = ExcelProcessor.clean_dataframe(df)
        
        series_dict = {}
        objects_to_create = []
        objects_to_update = {}
        
        # Extraer códigos de serie para consulta masiva
        all_series_codes = [
            str(row['codigo']).strip() 
            for _, row in df.iterrows() 
            if '.' in str(row['codigo'])
        ]
        
        # Buscar series existentes
        existing_series = {}
        if all_series_codes:
            for serie in Series.objects.filter(codigo_serie__in=all_series_codes):
                existing_series[serie.codigo_serie] = serie
        
        # Preparar objetos para creación/actualización masiva
        for _, row in df.iterrows():
            try:
                codigo = str(row['codigo']).strip()
                
                # Procesar solo si el formato del código es válido para una serie
                if '.' in codigo:
                    parts = codigo.split('.')
                    section_code = parts[0]  # Primera parte como código de sección
                    
                    series = str(row['series']).strip()
                    section = sections_dict.get(section_code)
                    
                    if section:
                        if codigo in existing_series:
                            objects_to_update[codigo] = {
                                'serie': series,
                                'descripcion': series,
                                'id_seccion': section,
                                'delete': False
                            }
                        else:
                            objects_to_create.append(
                                Series(
                                    codigo_serie=codigo,
                                    serie=series,
                                    descripcion=series,
                                    id_seccion=section,
                                    delete=False
                                )
                            )
            except Exception as e:
                logger.warning(f"Error procesando serie: {str(e)}")
                continue
        
        # Crear en masa
        if objects_to_create:
            created_series = Series.objects.bulk_create(objects_to_create)
            for serie in created_series:
                series_dict[serie.codigo_serie] = serie
                
        # Actualizar existentes
        if objects_to_update:
            for codigo, serie in existing_series.items():
                if codigo in objects_to_update:
                    updates = objects_to_update[codigo]
                    for key, value in updates.items():
                        setattr(serie, key, value)
                    serie.save()
                    series_dict[codigo] = serie
        
        return series_dict


class SubseriesProcessor:
    """Clase para procesar subseries de un archivo Excel."""
    
    @staticmethod
    def process_batch(df, series_dict):
        """Procesa un lote de subseries desde el DataFrame."""
        if df is None or df.empty:
            return
            
        df = ExcelProcessor.clean_dataframe(df)
        
        objects_to_create = []
        objects_to_update = {}
        
        # Extraer códigos de subserie para consulta masiva
        all_subserie_codes = []
        for _, row in df.iterrows():
            codigo = str(row['codigo']).strip()
            parts = codigo.split('.')
            if len(parts) >= 3:
                all_subserie_codes.append(codigo)
        
        # Buscar subseries existentes
        existing_subseries = {}
        if all_subserie_codes:
            for subserie in SubSerie.objects.filter(codigo_subserie__in=all_subserie_codes):
                existing_subseries[subserie.codigo_subserie] = subserie
        
        # Preparar objetos para creación/actualización masiva
        for _, row in df.iterrows():
            try:
                codigo = str(row['codigo']).strip()
                subserie = str(row['subserie']).strip()
                
                # Verificar si es un código de subserie (debe tener al menos dos puntos)
                parts = codigo.split('.')
                if len(parts) >= 3:
                    serie_code = '.'.join(parts[:-1])  # Todo excepto la última parte
                    
                    serie = series_dict.get(serie_code)
                    if serie:
                        if codigo in existing_subseries:
                            objects_to_update[codigo] = {
                                'subserie': subserie,
                                'descripcion': subserie,
                                'id_serie': serie,
                                'delete': False
                            }
                        else:
                            objects_to_create.append(
                                SubSerie(
                                    codigo_subserie=codigo,
                                    subserie=subserie,
                                    descripcion=subserie,
                                    id_serie=serie,
                                    delete=False
                                )
                            )
            except Exception as e:
                logger.warning(f"Error procesando subserie: {str(e)}")
                continue
        
        # Crear en masa
        if objects_to_create:
            SubSerie.objects.bulk_create(objects_to_create)
                
        # Actualizar existentes
        if objects_to_update:
            for codigo, subserie in existing_subseries.items():
                if codigo in objects_to_update:
                    updates = objects_to_update[codigo]
                    for key, value in updates.items():
                        setattr(subserie, key, value)
                    subserie.save()


class ImportExcelView(GenericViewSet):
    """ViewSet para importar datos desde archivos Excel."""
    serializer_class = ExcelUploadSerializer
    permission_classes = []  # Considerar añadir permisos adecuados en producción

    @action(detail=False, methods=['post'], url_path='upload')
    def import_excel(self, request):
        """
        Importa datos desde un archivo Excel.
        El archivo debe contener hojas para secciones, series y opcionalmente subseries.
        """
        # Iniciar una transacción manual para poder confirmarla o revertirla explícitamente
        try:
            # Validar los datos de entrada
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            file = serializer.validated_data['file']
            logger.info(f"Procesando archivo: {file.name}")

            # Encontrar las filas de inicio para cada sección (optimizado)
            section_start, series_start, subseries_start = ExcelProcessor.find_section_headers(file)

            # Usar varias transacciones más pequeñas en lugar de una grande
            with transaction.atomic():
                # Cargar secciones existentes para optimizar
                existing_sections = {s.codigo_seccion: s for s in Seccion.objects.all()}
                
                # Procesar secciones en chunks para evitar problemas de memoria
                file.seek(0)  # Volver al inicio del archivo
                df_sections = ExcelProcessor.read_excel_in_chunks(
                    file, 
                    skiprows=section_start - 1, 
                    usecols=['codigo', 'secciones']
                )
                df_sections = ExcelProcessor.validate_columns(df_sections, ['codigo', 'secciones'], 'Secciones')
                
                # Procesar en lotes
                sections_dict = BatchProcessor.process_in_batches(
                    df_sections, 
                    SectionProcessor.process_batch,
                    existing_sections=existing_sections
                )
                
                # Actualizar con todas las secciones para las series
                sections_dict.update(existing_sections)
            
            # Usar una nueva transacción para series
            with transaction.atomic():
                # Cargar series existentes para optimizar
                file.seek(0)
                df_series = ExcelProcessor.read_excel_in_chunks(
                    file, 
                    skiprows=series_start - 1,
                    usecols=['codigo', 'series']
                )
                df_series = ExcelProcessor.validate_columns(df_series, ['codigo', 'series'], 'Series')
                
                # Procesar series en lotes
                series_dict = BatchProcessor.process_in_batches(
                    df_series, 
                    SeriesProcessor.process_batch,
                    sections_dict=sections_dict
                )

            # Procesar subseries si existen, en una nueva transacción
            if subseries_start is not None:
                with transaction.atomic():
                    file.seek(0)
                    df_subseries = ExcelProcessor.read_excel_in_chunks(
                        file, 
                        skiprows=subseries_start - 1,
                        usecols=['codigo', 'subserie']
                    )
                    df_subseries = ExcelProcessor.validate_columns(df_subseries, ['codigo', 'subserie'], 'Subseries')
                    
                    # Procesar subseries en lotes
                    BatchProcessor.process_in_batches(
                        df_subseries, 
                        SubseriesProcessor.process_batch,
                        series_dict=series_dict
                    )

            return Response({'message': 'Importación completada exitosamente'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            logger.error(f"Error de validación: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return Response(
                {'error': f'Error procesando el archivo: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )