from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.menu, name='menu'),
    path('order-list/', views.order_list, name='order_list'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('cart/', views.cart, name='cart'),
]