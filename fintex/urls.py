"""
URL configuration for fintex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from exchange import views

urlpatterns = [
    path("", views.main, name="main"),
    path("api/get_rate/<str:currency_from>/<str:currency_to>", views.get_rate, name="api_rate"),
    path("api/chanel/<str:chanel>/<str:value>", views.main, name="static_content"),
    path("api/rates/<str:chanel>/<str:from_date>", views.main, name="history"),
    path("api/balance/<str:chanel>", views.main, name="api_rate"),
    path("api/get_currency_list/", views.get_currency_list, name="api_currency_list"),
    path("api/create_exchange_request/", views.create_exchange_request, name="api_create_exchange_request"),
    path('oper/', include('oper.urls')), #new
    path('admin/', admin.site.urls),
]
