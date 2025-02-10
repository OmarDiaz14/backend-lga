from django.db import models
from django.db.models import JSONField
from django.db import connection

class dashboard (models.Model):
    def obtener_total_series(id_seccion):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_total_series', [id_seccion])
            series = cursor.fetchall()
            
        colums = ["id_serie", "serie", "total"]
        series_dict = [dict(zip(colums, row)) for row in series]
        return series_dict
    
    def obtener_total_expedientes(id_seccion):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_total_expedientes', [id_seccion])
            total = cursor.fetchall()
            
            total_portadas = total[0][0] if total else 0
            return {"total_portadas": total_portadas}
        
    def obtener_total_fichas(id_seccion):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_total_fichas', [id_seccion])
            total = cursor.fetchall()
            
            total_fichas = total[0][0] if total else 0
            return {"total_fichas": total_fichas}
    
    def obtener_total_catalogos(id_seccion):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_total_catalogos', [id_seccion])
            total = cursor.fetchall()
            
            total_catalogos = total[0][0] if total else 0
            return {"total_catalogos": total_catalogos}
        
    