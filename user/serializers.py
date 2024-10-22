from rest_framework import serializers
from django.contrib.auth.models import User
from .models import User, Permiso, Roles 

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = "__all__"

class RolSerializer(serializers.ModelSerializer):
    permisos = PermisoSerializer(many=True, read_only=True)

    class Meta:
        model = Roles
        fields = '__all__' 


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(many=True, queryset=Roles.objects.all())

    class Meta:
        model = User
        fields = ['id','username','email','password','first_name',
                  'last_name','cargo','unidad_admi','roles','id_seccion']