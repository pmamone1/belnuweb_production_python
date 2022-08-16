from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('selected_order/<int:order_id>/', views.selected_order, name='selected_order'),
    path('borrar_pedido/<int:pk>/', views.borrar_pedido, name='borrar_pedido'),
    path('filtrar_pedido/', views.filtrar_pedido, name='filtrar_pedido'),
    path('filtrar_pedido/<str:filtro>/', views.filtrar_pedido, name='filtrar_pedido'),
    path('cumplir_pedidos/', views.cumplir_pedidos, name='cumplir_pedidos'),
    path('exporta_pedidos_xls/', views.exporta_pedidos_xls, name='exporta_pedidos_xls'),
    
]
