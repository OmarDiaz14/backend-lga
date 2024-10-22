from rest_framework import serializers
from .models import Seccion, Series, SubSerie



class SeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seccion
        fields = ('id_seccion','codigo','descripcion')
        


class SerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ('id_serie', 'serie', 'codigo_serie','descripcion','id_seccion')

    id_seccion = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), required=True)


class SubSerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubSerie
        fields = ('SubSerie', 'descripcion','serie')
    
    serie = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), required = True)