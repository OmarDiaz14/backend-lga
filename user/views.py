from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
#from django.contrib.auth.models import User
from .models import User
from rest_framework.authtoken.models import Token
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Roles
from .serializers import RolSerializer





# Create your views here.

class RolViewSet (viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RolSerializer



class IsAdminOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.id == request.user.id 
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]




@api_view (['POST'])
def login (request):
    
    user = get_object_or_404 (User, username = request.data['username'])
    
    if not user.check_password(request.data['password']):
        return Response({"error": "Invalid password"},status=status.
                        HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)


    return Response ({"token": token.key, "user": serializer.data}, status=status.
                     HTTP_200_OK)



@api_view (['POST'])
def register (request):
    serializer = UserSerializer(data = request.data)


    if serializer.is_valid():
        serializer.save()

        user = User.objects.get(username = serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()

        token = Token.objects.create(user=user)
        return Response({'token': token.key, "user":serializer.data },status=status.HTTP_201_CREATED)


    return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view (['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile (request):

   

    print(request.user)

    serializer = UserSerializer(instance = request.user)

    #return Response ("You are login with {}".format(request.user.username),
    #                 status=status.HTTP_200_OK)
    return Response(serializer.data,status=status.HTTP_200_OK )

