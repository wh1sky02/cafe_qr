
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from .models import MenuItem, Table, Category, Order, OrderSession, Banner, QRCode

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
    list_display = ('id', 'session', 'menu_item', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('menu_item__name', 'notes')

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'is_active', 'created_at')
    list_filter = ('is_active',)

# Set admin site header and title
admin.site.site_header = 'Cafe Administration'
admin.site.site_title = 'Cafe Admin Portal'
admin.site.index_title = 'Site administration'
