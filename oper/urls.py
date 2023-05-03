from django.urls import path
from . import views

urlpatterns = [
    path('', views.oper_home, name='oper_home'),
    path('oper_rate_settings/', views.rates_settings, name='oper_rate_settings'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout, name='logout'),
    path('try_login/', views.try_login, name='try_login'),
    path("api/save_rate/<str:from_currency>/<str:to_currency>", views.save_rate, name="setup_rate"),
    path("api/test_rate", views.test_rate, name="test_rate"),
    path("api/delete_rate/<str:from_currency>/<str:to_currency>", views.delete_rate, name="delete_rate"),
    path("to_history_page/<int:deal>/", views.to_history_page, name="to_history_page"),
    path("trans_page/", views.trans_page, name="trans_page"),


    path("api/telegram_subscribe/", views.telegram_subscribe, name="telegram_subscribe"),
    path("api/telegram_subscribe_callback/<str:token>/", views.telegram_subscribe_callback,
         name="telegram_subscribe_callback"),

    path("api/trans/", views.trans, name="trans_api"),
    path("api/chat_connect2deal", views.telegram2deal, name="telegram2deal"),
    path("api/get_deal_from_chat", views.deal2telegram, name="deal2telegram"),

    path("api/orders/<str:order_id>", views.whole_oper_info, name="whole_oper_info"),

    path("api/orders/", views.oper_orders, name="oper_orders"),
    path("api/get_history/<str:chat_id>/", views.get_history, name="get_history"),
    path("api/post/<str:chat_id>/", views.post_message, name="post_msg"),
    path("api/message_income/<str:chat_id>/", views.message_income, name="message_income"),

    path("api/trans/<str:status>/<str:trans_id>/", views.trans_status, name="trans_status"),
    path("api/order/show_payment/<str:order_id>/", views.show_payment, name="show_payment"),
    path("api/order/status/<str:status>/<str:order_id>/", views.order_status, name="oper_order_status"),
    path("api/get_direction/<str:from_currency>/<str:to_currency>", views.get_direction, name="get_direction"),

    path('reset_pwd_request', views.reset_pwd_request, name='reset_pwd_request')
]
