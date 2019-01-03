from django.conf.urls import url
from users import views as users_views
from rest_framework.authtoken import views as rest_framework_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Session Login
    url(r'^login/$', users_views.get_auth_token, name='login'),
    url(r'^get_auth_token/', users_views.CustomAuthToken.as_view()),
    url(r'^logout/', users_views.UserLogoutView.as_view()),
    #url(r'^get_auth_token/', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    url(r'^signup', users_views.my_signup),
    url(r'^signin', users_views.my_signin),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)