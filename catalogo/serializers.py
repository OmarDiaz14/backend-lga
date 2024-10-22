from rest_framework import serializers
from .models import Catalogo, destino_expe, type_access, valores_docu
from cuadro.models import Seccion, Series

class DestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = destino_expe
        fields = "__all__"


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = type_access
        fields = "__all__"

class ValoresSerializer(serializers.ModelSerializer):
    class Meta: 
        model = valores_docu
        fields = "__all__"


class CatalogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalogo
        fields = "__all__"

    id_seccion = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), required=True)
    id_serie = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), required=True)
    destino_expe = serializers.PrimaryKeyRelatedField(queryset=destino_expe.objects.all(),required=True)
    type_access = serializers.PrimaryKeyRelatedField(queryset=type_access.objects.all(), required=True)
    valores_documentales = serializers.PrimaryKeyRelatedField(queryset = valores_docu.objects.all(), required=True)
        
