from django.db import models
#from django.core.validators import MinLengthValidator

# Create your models here.

class GuiaDocu(models.Model):
    id_guia = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    volumen = models.IntegerField()
    ubicacion_fisica = models.CharField(max_length=100)
    serie = models.ForeignKey('cuadro.Series', on_delete=models.CASCADE,blank= False, null= True)
    seccion = models.ForeignKey('cuadro.Seccion', on_delete=models.CASCADE,blank=  False, null= True)
    num_expediente = models.ForeignKey('portada.portada', on_delete=models.CASCADE, blank= False, null= True)

    @property
    def fecha_inicio(self):
        if self.num_expediente:
            return self.num_expediente.fecha_apertura
        else:
            return None
        
        
    @property
    def fecha_fin(self):
        if self.num_expediente:
            return self.num_expediente.fecha_cierre
        else:
            return None


    