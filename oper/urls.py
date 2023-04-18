from django.urls import path
from . import views

urlpatterns = [
    path('', views.oper_home, name='oper_home'),
    path('oper_rate_settings/', views.rates_settings, name='oper_rate_settings'),
    path('login/', views.login_page, name='login_page'),
    path('try_login/', views.try_login, name='try_login'),
    path("api/save_rate/<str:from_currency>/<str:to_currency>", views.save_rate, name="setup_rate"),
    path("api/test_rate", views.test_rate, name="test_rate"),
    path("api/delete_rate/<str:from_currency>/<str:to_currency>", views.delete_rate, name="delete_rate"),

    path("api/orders/", views.oper_orders, name="oper_orders"),
    path("api/get_history/<str:deal>/", views.get_history, name="to_history"),
    path("api/to_history/<str:deal>/", views.to_history, name="chat_history_page"),
    path("api/order/<str:status>/<str:order_id>/", views.order_status, name="oper_order_status"),
    path("api/get_direction/<str:from_currency>/<str:to_currency>", views.get_direction, name="get_direction"),

    path('reset_pwd_request', views.reset_pwd_request, name='reset_pwd_request')
]
