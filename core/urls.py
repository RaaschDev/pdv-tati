from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mesas/', views.mesas, name='tables'),
    path('mesas/<str:table_id>/', views.table_detail, name='table_detail'),
    path('mesas/<str:table_id>/fechar/', views.close_order, name='close_order'),
    path('mesas/<str:table_id>/adicionar-produto/', views.add_order_item, name='add_order_item'),
    path('produtos/', views.products, name='products'),
    path('produtos/criar/', views.create_product, name='create_product'),
    path('pedidos/', views.orders, name='orders'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
