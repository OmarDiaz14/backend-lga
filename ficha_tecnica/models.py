from django.db import models
from django.db import connection


# Create your models here.

class FichaTecnica(models.Model):
    id_ficha = models.AutoField(primary_key=True)
    ficha = models.CharField(max_length=150)
    area_resguardante = models.CharField(max_length= 250)
    area_intervienen = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=250)
    soporte_docu = models.CharField(max_length=250)
    topologia = models.CharField(max_length=250)
    catalogo = models.ForeignKey('catalogo.Catalogo', on_delete=models.CASCADE, null=True, blank= False)
    seccion = models.ForeignKey('cuadro.Seccion', on_delete=models.CASCADE,  null=True, blank=False)
    serie = models.ForeignKey('cuadro.Series', on_delete=models.CASCADE, null=True, blank=False)
    subserie = models.ForeignKey('cuadro.SubSerie', on_delete=models.CASCADE, null=True, blank=False)

    def obtener_ficha_seccion(id_seccion):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_ficha_seccion', [id_seccion])
            fichas = cursor.fetchall()
            
        colums = ["ficha","serie","descripcion", "area_resguardante", "area_intervienen"]
        fichas_dict = [dict(zip(colums, row)) for row in fichas]
        return fichas_dict

