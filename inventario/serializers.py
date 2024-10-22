from rest_framework import serializers
from .models import Inventario 
from portada.models import portada
from cuadro.models import Seccion, Series 

class InventarioSerializer (serializers.ModelSerializer):
  
    #soporte_docu = serializers.CharField(source='FichaTecnica.soporte_docu', read_only=True) 
    class Meta:
        model = Inventario
        fields = ['num_consecutivo','serie', 'descripsion' ,
                   'observaciones','expediente','num_expediente','fecha_inicio','fecha_fin', 'legajos', 'fojas','valores_primarios', 'soporte', 'destino', 'acceso', 'estatus']
    #seccion = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), required=True)
    serie = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), required=True)
    expediente = serializers.PrimaryKeyRelatedField(queryset=portada.objects.all(),required =True )
    #fecha_inicio = serializers.PrimaryKeyRelatedField(queryset=portada.objects.all(),required =True )
    #fecha_fin = serializers.PrimaryKeyRelatedField(queryset=portada.objects.all(),required =True )
