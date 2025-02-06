from rest_framework import serializers

class DashboardSerializer(serializers.Serializer):
    id_serie = serializers.IntegerField()
    serie = serializers.CharField()
    total = serializers.IntegerField()