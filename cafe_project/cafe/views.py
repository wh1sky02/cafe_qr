from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from .models import MenuItem, Table, Category
import qrcode
import json
from io import BytesIO

# --------------------- Public Views ---------------------

def home(request):
    return render(request, 'home.html')

def menu(request):
    categories = Category.objects.all()
    menu_items = MenuItem.objects.all()
    return render(request, 'menu.html', {'categories': categories, 'menu_items': menu_items})

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


# --------------------- Authentication Views ---------------------

def custom_login(request):
    """Handles admin login"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")  # ✅ Redirect to the admin dashboard
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "admin_panel/login.html")

def custom_logout(request):
    """Logs out the user and redirects to the login page"""
    logout(request)
    return redirect("login")


# --------------------- Admin Panel Views ---------------------

@login_required
def dashboard(request):
    """Displays the Admin Dashboard"""
    return render(request, "admin_panel/dashboard.html")

@login_required
def dashboard_data(request):
    """Provides JSON data for the dashboard (Total, Active, and Inactive Tables)"""
    total_tables = Table.objects.count()
    active_tables = Table.objects.filter(is_active=True).count()
    inactive_tables = Table.objects.filter(is_active=False).count()

    return JsonResponse({
        "total_tables": total_tables,
        "active_tables": active_tables,
        "inactive_tables": inactive_tables
    })

@login_required
def qr_code_management(request):
    """Displays the QR Code Management page."""
    tables = Table.objects.all().order_by('number')
    return render(request, 'admin_panel/qr_code.html', {'tables': tables})

@csrf_exempt
@login_required
def generate_qr_code(request):
    """Generates a QR Code for a given table number."""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            table_number = data.get("table_number")

            if not table_number:
                return JsonResponse({'success': False, 'error': 'Table number is required'})

            # ✅ If table was removed before, re-create it
            table, created = Table.objects.get_or_create(number=table_number)

            # ✅ Always generate a new QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f'http://yourcafe.com/menu/{table.number}/')
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")  # Ensure format is PNG

            filename = f'table_{table.number}_qr.png'  # Ensure filename has .png extension
            table.qr_code.save(filename, File(buffer), save=False)
            table.save()

            return JsonResponse({
                'success': True,
                'table_number': table.number,
                'qr_code_url': table.qr_code.url,
                'status': 'active' if table.is_active else 'inactive'
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def remove_qr_code(request):
    """Deletes the entire table entry when removing QR code"""
    if request.method == "POST":
        data = json.loads(request.body)
        table_number = data.get("table_number")

        try:
            table = Table.objects.get(number=table_number)
            table.delete()  # Deletes the table entry entirely
            return JsonResponse({'success': True})
        except Table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Table not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
