from django.shortcuts import render, get_object_or_404
from .models import MenuItem

# Create your views here.
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html')


def menu(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'menu.html', {'menu_items': menu_items})

def order_list(request):
    return render(request, 'order_list.html')

def item_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    return render(request, 'item_detail.html', {'item': item})

def cart(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'cart.html', {'menu_items': menu_items})