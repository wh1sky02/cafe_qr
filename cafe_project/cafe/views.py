from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
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

def checkout(request):
    return render(request, 'checkout.html')

def generate_qr_code(request):
    if request.method == 'POST':
        table_number = request.POST.get('table_number')
        try:
            # Create or get table
            table, created = Table.objects.get_or_create(number=table_number)
            
            # Generate QR code
            table.generate_qr_code()
            table.save()
            
            return JsonResponse({
                'success': True,
                'qr_code_url': table.qr_code.url,
                'table_number': table.number
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})