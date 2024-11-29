from rest_framework import serializers
from .models import portada
from ficha_tecnica.models import FichaTecnica
from cuadro.models import Seccion, Series 
from catalogo.models import Catalogo


class portadaSerializer (serializers.ModelSerializer):
    #soporte_docu = serializers.CharField(source='FichaTecnica.soporte_docu', read_only=True) 
    class Meta:
        model = portada
        fields = '__all__'

        read_only_fields = ('num_expediente',) # No permite editar el numero de expediente

    seccion = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), required=True)
    serie = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), required=True)
    ficha = serializers.PrimaryKeyRelatedField(queryset=FichaTecnica.objects.all(),required =True)
    catalogo = serializers.PrimaryKeyRelatedField(queryset=Catalogo.objects.all(),required=True)