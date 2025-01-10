from rest_framework import serializers
from .models import FichaTecnica
from catalogo.models import Catalogo
from cuadro.models import Seccion, Series 
from catalogo.serializers import CatalogoSerializer


class FichaTecSerializer(serializers.ModelSerializer):
    catalogo_details = serializers.SerializerMethodField()

    class Meta:
        model = FichaTecnica
        fields = '__all__'
    
    # id_seccion = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), required=True)
    # id_serie = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), required=True)
    
    # def get_catalogo_details(self, obj):
    #     if obj.id_serie:
    #         catalogo = Catalogo.objects.filter(id_serie=obj.id_serie).first()
    #         return CatalogoSerializer(catalogo).data if catalogo else None
    #     return None
    
    def get_catalogo_details(self, obj):
        if obj.catalogo:
            return CatalogoSerializer(obj.catalogo).data
        return None
    
    def create(self, validated_data):
        serie = validated_data.get('id_serie')
        if serie:
            catalogo = Catalogo.objects.filter(id_serie=serie).first()
            if catalogo:
                validated_data['catalogo'] = catalogo
        return super().create(validated_data)
