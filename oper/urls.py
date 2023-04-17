from django.urls import path
from . import views

urlpatterns = [
    path('', views.rates_settings, name='oper_home'),
    path('oper_rate_settings/', views.rates_settings, name='oper_rate_settings'),
    path('login/', views.login_page, name='login_page'),
    path('try_login/', views.try_login, name='try_login'),
    path("api/save_rate/<str:from_currency>/<str:to_currency>", views.save_rate, name="setup_rate"),
    path("api/test_rate", views.test_rate, name="test_rate"),
    path("api/delete_rate/<str:from_currency>/<str:to_currency>", views.delete_rate, name="delete_rate"),
    path("api/get_direction/<str:from_currency>/<str:to_currency>", views.get_direction, name="get_direction"),
    path('reset_pwd_request', views.reset_pwd_request, name='reset_pwd_request')
]
