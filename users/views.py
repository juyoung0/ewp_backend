from django.shortcuts import render, redirect
from .forms import UserForm
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, generics, permissions
from users.permissions import IsAuthenticatedOrCreate
from users.serializers import SignUpSerializer
from django.contrib.auth import authenticate, login as django_login, get_user_model, logout as django_logout
from users.serializers import UserSerializer, GroupSerializer
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
import json

class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (IsAuthenticatedOrCreate,)

# Create the API views
class UserList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetails(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['groups']
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        django_login(request, user)
        token, created = Token.objects.get_or_create(user=user) #없으면 만들고, 있으면 가져오고
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email
        })

class UserLogoutView(APIView):
    """
    로그인한 사용자가 로그아웃 버튼을 누르면 토큰을 삭제하고
    사용자를 로그아웃시킨다.
    """
    def logout(self, request):
        """인스턴스 메서드로 토큰을 지우는 logout 메서드 정의"""
        try:
            request.user.auth_token.delete()
        except (ObjectDoesNotExist, AttributeError):
            content = {
                "detail": "토큰이 존재하지 않습니다."
            }
            django_logout(request)
            return Response(content, status=status.HTTP_200_OK)
        django_logout(request)
        content = {
            "detail": "성공적으로 로그아웃되었습니다.",
        }
        return Response(content, status=status.HTTP_200_OK)

    def get(self, request):
        """
        get요청으로 logout 인스턴스 메서드를 실행.
        """
        return self.logout(request)

@csrf_exempt
def get_auth_token(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        # the password verified for the user
        if user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            request.session['auth'] = token.key
            return redirect('/users/', request)
    return redirect('/users/auth/', request)

@csrf_exempt
def my_signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)

        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            login(request, new_user)
            return HttpResponse(json.dumps({'success':True, 'detail':request.POST}),content_type="application/json")
        return HttpResponse(json.dumps({'success':False}),content_type="application/json")

@csrf_exempt
def my_signin(request) :
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(json.dumps({'success':True, 'detail':request.POST}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'success':False}),content_type="application/json")

@csrf_exempt
def show_users(request):
    User = get_user_model()
    User.objects.all()

# 사용자 목록을 화면에 뿌려주는 ViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
