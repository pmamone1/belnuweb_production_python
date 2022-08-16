from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    #path('payments/', views.payments, name='payments'),
    path('order_complete/<str:user>/<str:user_id>/<str:user_email>/<str:numero_vendedor>/<str:grand_total>/<str:nombre_vendedor>/<str:nombre_completo>/<str:numero_pedido>/<str:status>/<str:fecha>/', views.order_complete, name='order_complete'),
    path('order_recived_email/<str:ordered_products>/<str:grand_total>/<str:numero_vendedor>/<str:nombre_vendedor>/<str:numero_pedido>/<str:status>/', views.order_recived_email, name='order_recieved_email'),
]
