from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from .models import MenuItem, Table, Category, Order, OrderSession, Banner, QRCode, Cart, OrderDetail, Payment

# Unregister default models
admin.site.unregister(Group)
admin.site.unregister(User)

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('table', 'token', 'created_at')
    readonly_fields = ('token',)

# Authentication and Authorization section
class CustomGroupAdmin(GroupAdmin):
    pass

class CustomUserAdmin(UserAdmin):
    pass

admin.site.register(Group, CustomGroupAdmin)
admin.site.register(User, CustomUserAdmin)

# Cafe section
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')

@admin.register(OrderSession)
class OrderSessionAdmin(admin.ModelAdmin):
    list_display = ('table', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'total_price', 'order_status', 'payment_status', 'created_at')
    list_filter = ('order_status', 'payment_status', 'created_at')
    search_fields = ('table__number',)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'is_active', 'created_at')
    list_filter = ('is_active',)

# Set admin site header and title
admin.site.site_header = 'Cafe Administration'
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('table', 'menu_name', 'qty', 'price', 'total_price', 'created_at')
    search_fields = ('menu_name', 'table__number')

@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_name', 'table_number', 'qty', 'price', 'total_price')
    search_fields = ('menu_name', 'order__id', 'table_number')
    list_filter = ('table_number',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('payment_method', 'payment_status')

admin.site.site_title = 'Cafe Admin Portal'
admin.site.index_title = 'Site administration'
