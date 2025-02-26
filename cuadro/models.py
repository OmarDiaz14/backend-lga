from django.db import models
from django.db import connection
# Create your models here.


class Seccion(models.Model):
    id_seccion =  models.AutoField(primary_key=True)
    codigo_seccion = models.CharField(max_length=50)
    seccion = models.TextField() 
    descripcion = models.TextField(null= True) 
    delete = models.BooleanField(default=False)

class Series(models.Model):
    id_serie =  models.AutoField(primary_key=True)
    codigo_serie= models.CharField(max_length=50)
    serie = models.TextField() 
    descripcion = models.TextField(null= True) 
    id_seccion = models.ForeignKey('Seccion', on_delete=models.CASCADE, db_column='id_seccion', blank=True, null=True)
    delete = models.BooleanField(default=False)
    
    def obtener_series_seccion(id_seccion):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_series_seccion', [id_seccion])
            series = cursor.fetchall()
            
        colums = ["codigo_serie", "serie", "seccion"]
        series_dict = [dict(zip(colums, row)) for row in series]
        return series_dict
     
class SubSerie(models.Model):
    id_subserie =  models.AutoField(primary_key=True)
    codigo_subserie = models.CharField(max_length=50)
    subserie = models.TextField()
    descripcion = models.TextField(null= True) 
    id_serie = models.ForeignKey('Series', on_delete=models.CASCADE, db_column='id_serie', blank= True, null= True)
    delete = models.BooleanField(default=False)
    
    def obtener_subseries_seccion(id_seccion):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_subseries_seccion', [id_seccion])
            subseries = cursor.fetchall()
            
        colums = ["codigo_subserie", "subserie", "serie"]
        subseries_dict = [dict(zip(colums, row)) for row in subseries]
        return subseries_dict
    

    
