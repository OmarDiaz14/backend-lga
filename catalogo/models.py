from django.db import models
from django.db import connection

class destino_expe (models.Model):
    id_destino = models.AutoField(primary_key= True)
    destino = models.CharField(max_length=100, null= False)

class type_access (models.Model):
    id_type = models.AutoField(primary_key= True)
    type = models.CharField(max_length=100, null= False,)


class valores_docu (models.Model):
    id_valores = models.AutoField (primary_key= True )
    valores = models.CharField(max_length= 100, null= False)

class Catalogo(models.Model):
    id_catalogo = models.AutoField(primary_key= True)
    catalogo = models.CharField(max_length=50 )
    archivo_tramite = models.CharField(max_length=50)
    archivo_concentracion = models.CharField(max_length=50)
    observaciones = models.CharField(max_length=250, blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    destino_expe = models.ForeignKey('destino_expe',on_delete=models.CASCADE, null= False)
    type_access = models.ForeignKey('type_access', on_delete=models.CASCADE, null= False)
    valores_documentales = models.ForeignKey('valores_docu', models.DO_NOTHING, null= False)
    seccion = models.ForeignKey('cuadro.Seccion', on_delete=models.CASCADE, blank= False, null= True)
    serie = models.ForeignKey('cuadro.Series', on_delete=models.CASCADE,blank= False, null= True)
    subserie = models.ForeignKey('cuadro.SubSerie', on_delete=models.CASCADE, blank=True, null=True)

    def obtener_catalogo_seccion(id_seccion):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_catalogo_seccion', [id_seccion])
            catalogo = cursor.fetchall()
            
        colums = ["seccion", "serie", "valores_docu", "archivo_tramite", "archivo_concentracion", "type_access", "destino_expe"]
        catalogo_dict = [dict(zip(colums, row)) for row in catalogo]
        return catalogo_dict

on_delete=models.CASCADE


# Create your models here.