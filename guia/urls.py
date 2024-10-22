from rest_framework import routers
from .views import GuiaViewSet
from django.urls import path, include

router = routers.DefaultRouter()

router.register(r'guia_doc', GuiaViewSet)

urlpatterns = [
    path('', include (router.urls)),
]