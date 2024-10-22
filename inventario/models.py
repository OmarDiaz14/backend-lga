from django.db import models
#from portada.models import Portada

# Create your models here.

class Inventario(models.Model):
    num_consecutivo = models.AutoField(primary_key=True)
    serie = models.ForeignKey('cuadro.Series', on_delete=models.CASCADE, null= True, blank=True)
    descripsion = models.CharField(max_length=250) # Revisar en que tabla se saca la informacion de la descripsion 
    observaciones = models.CharField(max_length=250, blank=True, null=True)
    expediente = models.ForeignKey('portada.portada', on_delete=models.CASCADE, null= True, blank= True )
    VALORES_ESTATUS = [
        ('abierto', 'Abierto'),
        ('cerrado', 'Cerrado'),
    ]
    estatus = models.CharField(max_length=15, choices=VALORES_ESTATUS, default='abierto', )
    
    @property
    def num_expediente(self):
        if self.expediente:
            return self.expediente.num_expediente
        else:
            return None
    
    @property
    def fecha_inicio(self):
        if self.expediente:
            return self.expediente.fecha_apertura
        else:
            return None
        
        
    @property
    def fecha_fin(self):
        if self.expediente:
            return self.expediente.fecha_cierre
        else:
            return None
    
    @property
    def legajos(self):
        if self.expediente:
            return self.expediente.num_legajos
        else:
            return None
    
    @property
    def fojas(self):
        if self.expediente:  
            return self.expediente.num_fojas
        else:
            return None
        

    @property
    def soporte (self):
        if self.expediente:
            return self.expediente.soporte_docu
        else:
            return None
    
    @property
    def acceso (self):
        if self.expediente:
            return self.expediente.type
        else:
            return None
        
    @property
    def valores_primarios(self):
        if self.expediente:  
            return self.expediente.valor
        else:
            return None
        
    @property
    def destino (self):
        if self.expediente:
            return self.expediente.destino
        else:
            return None
        
    