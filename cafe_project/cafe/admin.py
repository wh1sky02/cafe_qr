
from django.contrib import admin
from .models import MenuItem, Table, Category, Order, Banner

admin.site.register(MenuItem)
admin.site.register(Category)

admin.site.register(Table)
admin.site.register(Order)
admin.site.register(Banner)


