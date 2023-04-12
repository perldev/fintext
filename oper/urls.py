from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='oper_home'),
    path('login/', views.login_page, name='login_page'),
    path('try_login/', views.try_login, name='try_login'),
    path('reset_pwd_request', views.reset_pwd_request, name='reset_pwd_request')
]
