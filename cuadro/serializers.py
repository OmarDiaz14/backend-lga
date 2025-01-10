from rest_framework import serializers
from .models import Seccion, Series, SubSerie



class SeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seccion
        fields = ('id_seccion', 'seccion', 'codigo_seccion','descripcion', 'delete')
        


class SerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ( 'id_serie', 'serie','codigo_serie','descripcion','id_seccion', 'delete')

    id_seccion = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), required=True)


class SubSerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubSerie
        fields = ('id_subserie', 'subserie', 'codigo_subserie','descripcion','id_serie', 'delete')
    
    id_serie = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), required = True)  