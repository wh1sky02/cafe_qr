from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('order-list/', views.order_list, name='order_list'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Admin Panel Routes
    path('admin-panel/', views.dashboard, name='dashboard'),
    path('admin-panel/dashboard-data/', views.dashboard_data, name='dashboard_data'),
    path('admin-panel/qr-code/', views.qr_code_management, name='qr_code_management'),
    path('admin-panel/generate-qr-code/', views.generate_qr_code, name='generate_qr_code'),  # ✅ Corrected URL
    path('admin-panel/remove-qr-code/', views.remove_qr_code, name='remove_qr_code'),

    # Authentication Routes
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
]
