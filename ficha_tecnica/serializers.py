from rest_framework import serializers
from .models import FichaTecnica
from cuadro.models import Seccion, Series 


class FichaTecSerializer(serializers.ModelSerializer):
    class Meta:
    

        model = FichaTecnica
        fields = ('id_ficha','area_resguardante', 'area_intervienen', 'descripcion', 
                  'soporte_docu', 'id_seccion','id_serie','id_subserie')
    
    id_seccion = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), required=True)
    id_serie = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), required=True)
    
