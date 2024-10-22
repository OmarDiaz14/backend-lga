from . import views
from django.urls import path, re_path
from .views import RolViewSet

rol_list = RolViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

rol_detail = RolViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    re_path('login',views.login),
    re_path('register',views.register),     
    re_path('profile',views.profile), 
    path('roles', rol_list, name='role-list'),
    path('roles/<int:pk>', rol_detail, name='role-detail'),

]
