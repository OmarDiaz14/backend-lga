from django.db import models
from django.db.models import JSONField
from django.db import connection
# Create your models here.

class portada (models.Model):

    Valor = [
        ('informativo', 'Informativo'),
        ('evidencial', 'Evidencial'),
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

    alfresco_response = JSONField(null=True, blank=True)
    documento_ruta = models.CharField(max_length=255, null=True, blank=True)
    documento_id = models.CharField(max_length=100, null=True, blank=True)


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
    def valor_primario(self):
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
        
    def actualizar_alfresco(self, respuesta_alfresco):
        self.alfresco_response = respuesta_alfresco
        self.documento_ruta = respuesta_alfresco.get('Ruta')
        self.documento_id = respuesta_alfresco.get('DocumentId')
        self.save()

    def save(self, *args, **kwargs):
        if not self.num_expediente:
            if self.serie and self.serie.codigo_serie:
                #Crea el numero de expediente pero basado con el codigo de serie
                prefix = f"{self.serie.codigo_serie}" #codigo de serie

            else:
                prefix = "GENERAL" #Se ingresa General si no hay una serie
            
            #Agrega el year y un contador unico 
            year = self.fecha_apertura.year
            count = portada.objects.filter(
                fecha_apertura__year=year,
                serie = self.serie
            ).count() + 1
            #Fromato del num de expe

            self.num_expediente = f"{prefix}.{year}.{count:04d}" #Exple: "Serie-2004-0001"
        super().save(*args, **kwargs)

    def obtener_portada_seccion(seccion):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_portadas_seccion', [seccion])
            portadas = cursor.fetchall() 
        
        columns = ["id_expediente", "num_expediente", "asunto", "f_apertura", "f_cierre", "ficha", "catalogo"]
        portadas_dict = [dict(zip(columns, row)) for row in portadas]
        return portadas_dict
    
    def obtener_expediente(num_exp):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_portada_exp', [num_exp])
            portadas = cursor.fetchall() 
        
        columns = ["id_expediente", "num_expediente", "asunto", "f_apertura", "f_cierre", "ficha", "catalogo"]
        portadas_dict = [dict(zip(columns, row)) for row in portadas]
        return portadas_dict
    
    def obtener_portada_asunto(asunto):
        with connection.cursor() as cursor:
            cursor.callproc('obtener_portada_asunto', [asunto])
            portadas = cursor.fetchall() 
        
        columns = ["id_expediente", "num_expediente", "asunto", "f_apertura", "f_cierre", "ficha", "catalogo"]
        portadas_dict = [dict(zip(columns, row)) for row in portadas]
        return portadas_dict

        