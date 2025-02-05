from django.db import models

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
     
class SubSerie(models.Model):
    id_subserie =  models.AutoField(primary_key=True)
    codigo_subserie = models.CharField(max_length=50)
    subserie = models.TextField()
    descripcion = models.TextField(null= True) 
    id_serie = models.ForeignKey('Series', on_delete=models.CASCADE, db_column='id_serie', blank= True, null= True)
    delete = models.BooleanField(default=False)
    
    
