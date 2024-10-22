from django.db import models

# Create your models here.

class portada (models.Model):

    Valor = [
        ('informativo', 'Informativo'),
        ('evidencial', 'Evidencia'),
        ('testimonial', 'Testimonial'),
    ]

    id_expediente = models.AutoField (primary_key= True)
    num_expediente = models.CharField(max_length=150)
    asunto = models.CharField(max_length=150)
    num_legajos = models.PositiveBigIntegerField(default=0)
    num_fojas = models.PositiveBigIntegerField(default=0)
    valores_secundarios = models.CharField(max_length=15, choices=Valor, default='informativo')
    fecha_apertura = models.DateField(null=False)
    fecha_cierre = models.DateField(null= True)
    seccion = models.ForeignKey('cuadro.Seccion',on_delete=models.CASCADE, null= True, blank= True)
    serie = models.ForeignKey('cuadro.Series', on_delete=models.CASCADE, null= True, blank=True)
    subserie = models.ForeignKey('cuadro.Subserie', on_delete=models.CASCADE, null = True, blank=True )
    ficha = models.ForeignKey('ficha_tecnica.FichaTecnica', on_delete=models.CASCADE, null= True, blank= True )
    catalogo = models.ForeignKey('catalogo.Catalogo', on_delete=models.CASCADE, null= True, blank= True)



    @property
    def  soporte_docu(self):
        if self.ficha:  
            return self.ficha.soporte_docu
        else:
            return None
        
    @property 
    def destino(self):
        if self.catalogo:
            return self.catalogo.destino_expe.destino
        else:
            return None
    @property
    def valor(self):
        if self.catalogo:
            return self.catalogo.valores_documentales.valores
        else:
            return None
        
    @property
    def type(self):
        if self.catalogo:
            return self.catalogo.type_access.type
        else:
            return None
        
    @property
    def archivo_tramite(self):
        if self.catalogo:
            return self.catalogo.archivo_tramite.archivo_tramite
        else:
            return None
        
    @property
    def archivo_concentracion(self):
        if self.catalogo:
            return self.catalogo.archivo_concentracion.archivo_concentracion
        else:
            return None