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
from django.contrib.auth import update_session_auth_hash

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


# --------------------- Admin Panel Views ---------------------
@login_required
def admin_menu(request):
    """Displays the admin menu management page"""
    menu_items = MenuItem.objects.all().order_by('category', 'name')
    categories = Category.objects.all()
    return render(request, 'admin_panel/menu_settings.html', {
        'menu_items': menu_items,
        'categories': categories
    })


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

@login_required
def settings(request):
    """Displays the settings page"""
    return render(request, "admin_panel/settings.html")

@login_required
def menu_settings(request):
    """Displays the menu settings page"""
    menu_items = MenuItem.objects.all().order_by('-status', 'name')
    categories = Category.objects.all()
    return render(request, "admin_panel/menu_settings.html", {'menu_items': menu_items, 'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        try:
            Category.objects.create(name=name)
            messages.success(request, 'Category added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding category: {str(e)}')
    return redirect('menu_settings')

@login_required
def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, 'Category deleted successfully!')
    except Category.DoesNotExist:
        messages.error(request, 'Category not found')
    except Exception as e:
        messages.error(request, f'Error deleting category: {str(e)}')
    return redirect('menu_settings')

@login_required
def edit_menu_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(MenuItem, id=item_id)
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.price = request.POST.get('price')
        item.category_id = request.POST.get('category')
        item.status = request.POST.get('status')
        
        if 'image' in request.FILES:
            item.image = request.FILES['image']
        
        item.save()
        messages.success(request, 'Menu item updated successfully!')
        return redirect('menu_settings')

@login_required
def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    messages.success(request, 'Menu item deleted successfully!')
    return redirect('menu_settings')

@login_required
def add_menu_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        status = request.POST.get('status')
        image = request.FILES.get('image')

        category = Category.objects.get(id=category_id)
        menu_item = MenuItem.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
            status=status,
            image=image
        )
        messages.success(request, 'Menu item added successfully!')
        return redirect('menu_settings')

@login_required
def change_password(request):
    """Handles password change"""
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords don't match.")
        else:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully.")
            update_session_auth_hash(request, user)  # Keep user logged in
            return redirect('settings')

    return redirect('settings')