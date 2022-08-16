from django.urls import path
from . import views
from .api import VariationApiView

urlpatterns = [
    path('', views.store, name="store"),
    path('category/<slug:category_slug>/', views.store, name='product_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:category_slug>/<slug:product_slug>/<int:edicion>/', views.product_detail_2, name='product_detail_2'),
    path('search/', views.search, name='search'),
    path('buscar_titulo/<int:product>/<int:edicion>/',VariationApiView.as_view(),name="variation_api"), # url para ajax de buscar titulo + edicion
    path('get_ajax_titulo/', views.get_ajax_titulo , name = "get_ajax_titulo"), # url para ajax de buscar titulo
    path('nuevo_producto/', views.nuevo_producto, name='nuevo_producto'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]
