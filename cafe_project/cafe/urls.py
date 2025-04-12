from django.urls import path
from . import views
from .views import order_status

urlpatterns = [
    path('update-cart-item/', views.update_cart_item, name='update_cart_item'),
     # Public Pages
     path('', views.home, name='home'),
     path('menu/<uuid:token>/', views.menu, name='menu'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
     path('order-list/', views.order_list, name='order_list'),
     path('item/<int:item_id>/', views.item_detail, name='item_detail'),
     path('cart/', views.cart, name='cart'),
     path('order-status/', order_status, name='order_status'),
     path('checkout/', views.checkout, name='checkout'),
     path('payment/', views.payment, name='payment'),
     path('order-confirmation/',
          views.order_confirmation,
          name='order_confirmation'),  # Added order confirmation URL

     # Admin Panel Routes
     path('admin-panel/', views.dashboard, name='dashboard'),
     path('admin-panel/dashboard-data/',
          views.dashboard_data,
          name='dashboard_data'),
     path('admin-panel/tables/', views.move_table, name='tables'),
     path('admin-panel/toggle-table-status/', views.toggle_table_status, name='toggle_table_status'),
     path('admin-panel/delete-table/', views.delete_table, name='delete_table'),
     path('admin-panel/qr-code/',
          views.qr_code_management,
          name='qr_code_management'),
     path('admin-panel/generate-qr-code/',
          views.generate_qr_code,
          name='generate_qr_code'),
     path('admin-panel/remove-qr-code/',
          views.remove_qr_code,
          name='remove_qr_code'),
     path('admin-panel/orders/', views.orders_page, name='orders'),
     path('admin-panel/order-details/<int:order_id>/', views.order_details, name='order_details'),
     path('admin-panel/update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
     path('admin-panel/filter-orders/', views.filter_orders, name='filter_orders'),
     path('admin-panel/transactions/', views.transactions_view, name='transactions'),
     path('admin-panel/transaction-details/<int:transaction_id>/', views.transaction_details, name='transaction_details'),
     path('admin-panel/filter-transactions/', views.filter_transactions, name='filter_transactions'),

     # Authentication Routes
     path('login/', views.custom_login, name='login'),
     path('logout/', views.custom_logout, name='logout'),
     path('admin-panel/settings/', views.settings, name='settings'),
     path('admin-panel/change-password/',
          views.change_password,
          name='change_password'),
     path('admin-panel/menu-settings/',
          views.menu_settings,
          name='menu_settings'),
     path('admin-panel/menu/', views.admin_menu, name='admin_menu'),
     path('admin-panel/add-menu-item/',
          views.add_menu_item,
          name='add_menu_item'),
     path('admin-panel/add-category/', views.add_category, name='add_category'),
     path('admin-panel/delete-category/<int:category_id>/',
          views.delete_category,
          name='delete_category'),
     path('admin-panel/edit-menu-item/<int:item_id>/',
          views.edit_menu_item,
          name='edit_menu_item'),
     path('admin-panel/delete-menu-item/<int:item_id>/',
          views.delete_menu_item,
          name='delete_menu_item'),

     #Kitchen Routes
     path('kitchen_login/', views.kitchen_login, name='kitchen_login'),
     path('kitchen_dashboard/', views.kitchen_dashboard, name='kitchen_dashboard'),
     path('update_order_status/<int:order_id>/', views.update_order_status, name='kitchen_update_order_status'),

]