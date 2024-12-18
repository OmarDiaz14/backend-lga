from rest_framework import serializers
from .models import portada
from ficha_tecnica.models import FichaTecnica
from cuadro.models import Seccion, Series 
from catalogo.models import Catalogo
from ficha_tecnica.serializers import FichaTecSerializer
from catalogo.serializers import CatalogoSerializer



class portadaSerializer (serializers.ModelSerializer):
    ficha_details = serializers.SerializerMethodField()
    catalogo_details = serializers.SerializerMethodField()

    class Meta:
        model = portada
        fields = ['id_expediente','num_expediente','asunto','num_legajos','num_fojas','valores_secundarios','fecha_apertura','fecha_cierre','soporte_docu','destino', 'valor_primario','type','archivo_tramite', 'archivo_concentracion','seccion','serie','subserie','ficha','catalogo','alfresco_response','documento_ruta', 'documento_id','catalogo_details','ficha_details']
        read_only_fields = ('num_expediente','alfresco_response', 'documento_id','documento_ruta') # No permite editar el numero de expediente

    seccion = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), required=True)
    serie = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all(), required=True)
    #ficha = serializers.PrimaryKeyRelatedField(queryset=FichaTecnica.objects.all(),required =True)
    #catalogo = serializers.PrimaryKeyRelatedField(queryset=Catalogo.objects.all(),required=True)

    def get_ficha_details(self, obj):
        if obj.serie:
            ficha = FichaTecnica.objects.filter(id_serie=obj.serie).first()  
            return FichaTecSerializer(ficha).data if ficha else None
        return None
    
    def get_catalogo_details(self, obj):
        if obj.serie:
            catalogo = Catalogo.objects.filter(id_serie=obj.serie).first()
            return CatalogoSerializer(catalogo).data if catalogo else None
        return None 
    
    def create(self, validated_data):
        serie = validated_data.get('serie')
        if serie:
            ficha = FichaTecnica.objects.filter(id_serie=serie).first()
            if ficha:
                validated_data['ficha'] = ficha

            
            catalogo = Catalogo.objects.filter(id_serie=serie).first()
            if catalogo:
                validated_data['catalogo'] = catalogo
        
        return super().create(validated_data)
    
   
    