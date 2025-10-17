from django.urls import path
from apps.security.views import auth

app_name = 'security'

urlpatterns = [
    path('login/', auth.AdminLoginView.as_view(), name='login'),
    path('logout/', auth.AdminLogoutView.as_view(), name='logout'),
]