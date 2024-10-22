from django.db import models

# Create your models here.


class Seccion(models.Model):
    id_seccion =  models.CharField(max_length=250,primary_key=True)
    codigo = models.CharField(max_length=200) 
    descripcion = models.TextField() 

    

class Series(models.Model):
    id_serie = models.CharField(max_length=100)
    serie = models.CharField(max_length=150, primary_key=True)
    codigo_serie= models.TextField()
    descripcion = models.TextField()
    id_seccion = models.ForeignKey('Seccion', on_delete=models.CASCADE, db_column='seccion', blank=True, null=True)
       


class SubSerie(models.Model):
    SubSerie = models.CharField(max_length=150,primary_key=True)
    descripcion = models.TextField()
    serie = models.ForeignKey('Series', on_delete=models.CASCADE,blank= True, null= True)
    
