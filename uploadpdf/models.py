from django.db import models

# Create your models here.
class Documento (models.Model):
    seccion = models.CharField(max_length=255)
    serie = models.CharField(max_length= 50)
    serie_documental = models.CharField(max_length=255)
    contenido = models.TextField()


    def __str__(self):
        return f"{self.seccion} - {self.codigo}"