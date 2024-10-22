from rest_framework import serializers
from .models import GuiaDocu
from cuadro.models import Series, Seccion
from portada.models import portada


class GuiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuiaDocu
        fields = ['id_guia', 'descripcion', 'volumen', 'ubicacion_fisica',
                  'serie', 'seccion','num_expediente', 'fecha_inicio', 'fecha_fin' ]
    
    serie = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), required=True)
    seccion = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), required=True)
    num_expediente = serializers.PrimaryKeyRelatedField(queryset=portada.objects.all(), required = True)
    
    """extra_kwargs = {
            'serie': {'required': True}  # Se asegura de que sea obligatorio
        }
    
    def validate_serie(self, value):
        if value is None:
            raise serializers.ValidationError("El campo serie no puede estar vacío.")
        return value"""