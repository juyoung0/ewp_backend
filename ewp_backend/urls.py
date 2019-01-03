"""ewp_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
#from django.contrib.auth import view as auth_views
from django.urls import path
from rest_framework import routers, permissions
from mongo import views as mongo_views
from users import views as users_views
from mongo.views import MongoConnection

router = routers.DefaultRouter()
router.register(r'user', users_views.UserViewSet)

urlpatterns = [
    # 인증처리를 위한 url
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^users/', include(('users.urls', 'users'), namespace="users")),
    url(r'^api/', include(('mongo.urls', 'mongo'), namespace="mongo")),
    #url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('admin/', admin.site.urls),
    #path('users/', users_views.UserList.as_view()),
    #path('users/<pk>/', users_views.UserDetails.as_view()),
    #path('groups/', users_views.GroupList.as_view()),
]
