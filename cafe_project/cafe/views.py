from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
import uuid
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.utils.timezone import now
from django.db.models import Sum
from datetime import timedelta
from .models import MenuItem, Table, Category, Order, Banner, QRCode, Cart, OrderDetail, Payment # Added Payment import
import qrcode
import random
import json
from io import BytesIO
from django.contrib.auth import update_session_auth_hash
import string
import base64
import io
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime

# --------------------- Public Views ---------------------

def home(request):
    # Get first table's token or create a new table if none exists
    table = Table.objects.first()
    if not table:
        table = Table.objects.create(number=1)
    
    # Store the token in session if not already set
    if not request.session.get('table_token'):
        request.session['table_token'] = str(table.token)

    thirty_days_ago = now() - timedelta(days=30)
    new_items = MenuItem.objects.filter(created_at__gte=thirty_days_ago)[:3]

    # For now, just get random items as bestsellers
    all_items = list(MenuItem.objects.all())
    bestsellers = random.sample(all_items, min(3, len(all_items))) if all_items else []

    all_items = list(MenuItem.objects.all())
    recommended_items = random.sample(all_items, min(3, len(all_items))) if all_items else []

    banners = Banner.objects.all()
    
    # Get table token from session and calculate total qty for cart counter
    table_token = request.session.get('table_token')
    total_qty = 0
    if table_token:
        try:
            session_table = Table.objects.get(token=table_token)
            total_qty = Cart.objects.filter(table=session_table).aggregate(total=Sum('qty'))['total'] or 0
        except Table.DoesNotExist:
            pass

    return render(request, 'home.html', {
        'recommended_items': recommended_items,
        'bestsellers': bestsellers,
        'new_items': new_items,
        'banners': banners,
        'token': table.token,
        'total_qty': total_qty
    })

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_token = data.get('table_token')
        menu_name = data.get('menu_name')
        image = data.get('image')
        price = data.get('price')
        qty = data.get('qty', 1)

        table = get_object_or_404(Table, token=table_token)

        # Check if item already exists in cart
        cart_item = Cart.objects.filter(table=table, menu_name=menu_name).first()
        if cart_item:
            cart_item.qty += qty
            cart_item.save()
        else:
            Cart.objects.create(
                table=table,
                menu_name=menu_name,
                image=image,
                price=price,
                qty=qty
            )

        # Return cart count for this table
        cart_count = Cart.objects.filter(table=table).aggregate(
            total_items=Sum('qty')
        )['total_items'] or 0

        # Get item-specific count
        item_count = Cart.objects.get(table=table, menu_name=menu_name).qty

        return JsonResponse({
            'success': True, 
            'cart_count': cart_count,
            'item_count': item_count
        })
    return JsonResponse({'success': False})

def menu(request, token):
    # Lookup table by token
    table = get_object_or_404(Table, token=token)

    # Store the token in session
    request.session['table_token'] = str(token)

    categories = Category.objects.all()
    menu_items = MenuItem.objects.all()

    # Get cart counts for each menu item
    cart_items = Cart.objects.filter(table=table)
    cart_counts = {item.menu_name: item.qty for item in cart_items}

    # Get total quantity for cart counter
    total_qty = cart_items.aggregate(total=Sum('qty'))['total'] or 0

    return render(request, 'menu.html', {
        'table': table, 
        'categories': categories, 
        'menu_items': menu_items,
        'cart_counts': cart_counts,
        'cart_items': cart_items,
        'total_qty': total_qty
    })

def order_list(request):
    return render(request, 'order_list.html')

def item_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    # Get table token from session to keep it consistent across pages
    table_token = request.session.get('table_token')
    
    # Get total quantity for cart counter
    if table_token:
        table = Table.objects.get(token=table_token)
        total_qty = Cart.objects.filter(table=table).aggregate(total=Sum('qty'))['total'] or 0
    else:
        total_qty = 0
        
    return render(request, 'item_detail.html', {
        'item': item,
        'token': table_token,
        'total_qty': total_qty
    })

def cart(request):
    try:
        # Retrieve the token from session
        table_token = request.session.get('table_token')
        if not table_token:
            return redirect('home')

        table = Table.objects.get(token=table_token)

        # Get cart items for this table
        cart_items = Cart.objects.filter(table=table).order_by('created_at')
        total_price = sum(float(item.price) * item.qty for item in cart_items)
        
        # Get total quantity for cart counter
        total_qty = cart_items.aggregate(total=Sum('qty'))['total'] or 0

        return render(request, 'cart.html', {
            'cart_items': cart_items,
            'total_price': "{:.2f}".format(total_price),
            'token': table_token,
            'total_qty': total_qty
        })
    except Table.DoesNotExist:
        return redirect('home')

@csrf_exempt
def update_cart_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            new_qty = int(data.get('quantity', 0))

            if not item_id:
                return JsonResponse({'success': False, 'error': 'Invalid item ID'})

            cart_item = Cart.objects.get(id=item_id)

            if new_qty < 1:
                # Delete the item if quantity is 0
                cart_item.delete()
            else:
                cart_item.qty = new_qty
                cart_item.save()

            # Calculate new total price and cart count
            table = cart_item.table
            cart_items = Cart.objects.filter(table=table)
            total_price = sum(float(item.price) * item.qty for item in cart_items)
            cart_count = cart_items.aggregate(total=Sum('qty'))['total'] or 0

            return JsonResponse({
                'success': True,
                'total_price': "{:.2f}".format(total_price),
                'cart_count': cart_count,
                'item_qty': new_qty,
                'item_subtotal': "{:.2f}".format(float(cart_item.price) * new_qty)
            })
        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cart item not found'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid quantity value'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def checkout(request):
    table_token = request.session.get('table_token')
    if table_token:
        table = Table.objects.get(token=table_token)
        cart_items = Cart.objects.filter(table=table)
        subtotal = sum(item.price * item.qty for item in cart_items)
        total_qty = cart_items.aggregate(total=Sum('qty'))['total'] or 0

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'total_price': subtotal,
            'total_qty': total_qty
        })
    return redirect('home')

def payment(request):
    # Get table data and cart items
    table_token = request.session.get('table_token')
    if not table_token:
        return redirect('home')

    table = Table.objects.get(token=table_token)
    cart_items = Cart.objects.filter(table=table)
    
    # Calculate totals
    subtotal = sum(item.price * item.qty for item in cart_items)
    tax_amount = Decimal(str(subtotal)) * Decimal('0.09')
    total_amount = subtotal + tax_amount
    total_qty = cart_items.aggregate(total=Sum('qty'))['total'] or 0

    # For GET requests, just render the payment page without error
    if request.method == 'GET':
        return render(request, 'payment.html', {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'total_qty': total_qty
        })
    
    # Process POST request
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        tip_amount = Decimal(request.POST.get('tip_amount', '0'))
        tax_amount = Decimal(request.POST.get('tax_amount', '0'))
        total_amount = Decimal(request.POST.get('total_amount', '0'))
        note = request.POST.get('note', '')

        # Card details - in a real application, you would send these to a payment gateway
        card_number = request.POST.get('card_number')
        card_name = request.POST.get('card_name')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')
        
        # Debug output
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        print(f"Is AJAX request: {is_ajax}")
        print(f"Payment method: {payment_method}")
        print(f"Card number present: {'Yes' if card_number else 'No'}")
        
        # Only check for card details if payment method is 'card'
        if payment_method == 'card' and not card_number:
            error_msg = 'Card details are required'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg})
            else:
                error_msg = ''
                # Render the payment page with error
                return render(request, 'payment.html', {
                    'cart_items': cart_items,
                    'subtotal': subtotal,
                    'tax_amount': tax_amount,
                    'total_amount': total_amount,
                    'tip_amount': tip_amount,
                    'total_qty': total_qty,
                    'error': error_msg
                })

        try:
            # Validate empty cart
            if not cart_items.exists():
                error_msg = 'Your cart is empty. Please add items before checkout.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg})
                return redirect('menu')
                
            # Create order
            order = Order.objects.create(
                table=table,
                total_price=total_amount,
                order_status='pending',
                payment_status='paid'  # Always set to paid for card payments
            )

            # Create order details
            for cart_item in cart_items:
                item_subtotal = cart_item.price * cart_item.qty
                item_tip = Decimal('0')
                if tip_amount > 0 and cart_items.count() > 0:
                    item_tip = tip_amount / cart_items.count()
                
                OrderDetail.objects.create(
                    order=order,
                    menu_name=cart_item.menu_name,
                    image=cart_item.image,
                    qty=cart_item.qty,
                    price=cart_item.price,
                    subtotal=item_subtotal,
                    tip_amount=item_tip,
                    notes=note,
                    table_number=table.number,
                    total_price=item_subtotal + (tax_amount / cart_items.count() if cart_items.count() > 0 else Decimal('0')) + item_tip
                )

            # Create payment record
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                payment_status='paid'
            )

            # Clear cart after successful order creation
            cart_items.delete()

            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'order_id': order.id,
                    'total_amount': str(total_amount)
                })
            else:
                return redirect(f'/order-confirmation/?amount={total_amount}&order_id={order.id}')

        except Exception as e:
            error_message = str(e)
            print(f"Error processing order: {error_message}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'Payment failed: {error_message}'})
            else:
                return redirect('checkout')

    # Fallback response (should not reach here)
    return render(request, 'payment.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'total_qty': total_qty
    })


def order_confirmation(request):
    if request.method == 'POST':
        table_token = request.session.get('table_token')
        if not table_token:
            return redirect('home')
        
        try:
            table = Table.objects.get(token=table_token)
            cart_items = Cart.objects.filter(table=table)
            
            # Get values from POST data
            payment_method = request.POST.get('payment_method', 'cash')
            tip_amount = Decimal(request.POST.get('tip_amount', '0'))
            tax_amount = Decimal(request.POST.get('tax_amount', '0'))
            total_amount = Decimal(request.POST.get('total_amount', '0'))
            note = request.POST.get('note', '')
            
            # Create order
            order = Order.objects.create(
                table=table,
                total_price=total_amount,
                order_status='pending',
                payment_status='pending' if payment_method == 'cash' else 'paid'
            )
            
            # Create order details
            for cart_item in cart_items:
                item_subtotal = cart_item.price * cart_item.qty
                item_tip = tip_amount / len(cart_items) if tip_amount > 0 and len(cart_items) > 0 else Decimal('0')
                
                OrderDetail.objects.create(
                    order=order,
                    menu_name=cart_item.menu_name,
                    image=cart_item.image,
                    qty=cart_item.qty,
                    price=cart_item.price,
                    subtotal=item_subtotal,
                    gst_amount=tax_amount / len(cart_items) if len(cart_items) > 0 else Decimal('0'),
                    tip_amount=item_tip,
                    notes=note,
                    table_number=table.number,
                    total_price=item_subtotal + (tax_amount / len(cart_items) if len(cart_items) > 0 else Decimal('0')) + item_tip
                )
            
            # Create payment record
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                payment_status='pending' if payment_method == 'cash' else 'paid'
            )
            
            # Clear cart after successful order creation
            cart_items.delete()
            
            # Redirect with amount as query parameter for the confirmation page
            return redirect(f'/order-confirmation/?amount={total_amount}&order_id={order.id}')
            
        except Exception as e:
            print(f"Error processing order: {str(e)}")
            return redirect('checkout')
    
    # For GET requests - MVC approach: fetch order data from database when available
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order_details = OrderDetail.objects.filter(order=order)
            
            return render(request, 'order_confirmation.html', {
                'order': order,
                'order_details': order_details
            })
        except Order.DoesNotExist:
            pass
    
    # If no order_id or order not found, render the template without database data
    return render(request, 'order_confirmation.html')

def order_status(request):
    try:
        table_token = request.session.get('table_token')
        table = Table.objects.get(token=table_token)

        # Get latest order for this table
        order = Order.objects.filter(
            table=table
        ).order_by('-created_at').first()

        # Get total quantity for cart counter
        total_qty = Cart.objects.filter(table=table).aggregate(total=Sum('qty'))['total'] or 0

        if order:
            order_details = OrderDetail.objects.filter(order=order)

            context = {
                'order': order,
                'order_details': order_details,
                'order_status': order.order_status,
                'total_qty': total_qty
            }
            return render(request, "orderstatus.html", context)

    except (Table.DoesNotExist, Exception) as e:
        print(f"Error fetching order status: {str(e)}")

    return render(request, "orderstatus.html")

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

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "admin_panel/login.html")

        # Check if user exists in database
        user_exists = User.objects.filter(username=username).exists()
        if not user_exists:
            messages.error(request, f"User '{username}' does not exist in the database.")

        # Print all available users for debugging
        all_users = User.objects.all().values_list('username', flat=True)
        print(f"Available users in the database: {list(all_users)}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")  # Redirect to the admin dashboard
        else:
            messages.error(request, f"Authentication failed for '{username}'.")

            # Check if user exists but password is wrong
            if user_exists:
                messages.warning(request, "Username exists but password is incorrect.")

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

# --------------------- MOVE TABLE VIEW ---------------------
@login_required
def move_table(request):
    """Displays the Tables page."""
    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get("action")

        if action == "add":
            # Get the highest table number and add 1
            highest_table = Table.objects.order_by('-number').first()
            new_table_number = 1 if not highest_table else highest_table.number + 1
            Table.objects.create(number=new_table_number)
            return JsonResponse({'success': True})

        elif action == "toggle":
            table_number = data.get("table_number")
            try:
                table = Table.objects.get(number=table_number)
                table.is_active = not table.is_active
                table.save()
                return JsonResponse({'success': True})
            except Table.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Table not found'})

        elif action == "delete":
            table_number = data.get("table_number")
            try:
                table = Table.objects.get(number=table_number)
                table.delete()
                return JsonResponse({'success': True})
            except Table.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Table not found'})

    tables = Table.objects.all().order_by('number')
    return render(request, "admin_panel/tables.html", {'tables': tables})

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

            try:
                table = Table.objects.get(number=int(table_number))

                # Delete existing QR code image if it exists
                if hasattr(table, 'qr_code'):
                    if table.qr_code.image:
                        table.qr_code.image.delete(save=False)
                    table.qr_code.delete()

                # Create new QR code with new tokens
                table.token = uuid.uuid4()  # Generate new table token
                table.save()

                qr = QRCode(table=table)
                qr.token = uuid.uuid4()  # Generate new QR code token
                qr.generate_qr_code()
                qr.save()

                return JsonResponse({
                    'success': True,
                    'table_number': table.number,
                    'qr_code_url': table.qr_code.image.url,
                    'status': 'active' if table.is_active else 'inactive'
                })
            except Table.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Table not found'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def remove_qr_code(request):
    """Deletes QR code and its image file"""
    if request.method == "POST":
        data = json.loads(request.body)
        table_number = data.get("table_number")

        try:
            table = Table.objects.get(number=table_number)
            if hasattr(table, 'qr_code'):
                # Delete the image file first
                if table.qr_code.image:
                    table.qr_code.image.delete(save=False)
                # Then delete the QR code object
                table.qr_code.delete()
            return JsonResponse({'success': True})
        except Table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Table not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def delete_table(request):
    """Deletes a table and optionally renumbers remaining tables."""
    if request.method == "POST":
        data = json.loads(request.body)
        table_number = data.get("table_number")
        renumber = data.get("renumber", True)  # Default to True

        try:
            table = Table.objects.get(number=table_number)
            table.delete()

            if renumber:
                # Get all tables with higher numbers and decrement them
                tables = Table.objects.filter(number__gt=table_number).order_by('number')
                for t in tables:
                    t.number -= 1
                    t.save()

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
    menu_items = MenuItem.objects.all().order_by('name')
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
def admin_orders(request):
    """Display and manage orders in admin panel"""
    orders = Order.objects.exclude(status='completed').order_by('-created_at')

    # Get counts for order statuses
    pending_count = orders.filter(status='pending').count()
    preparing_count = orders.filter(status='preparing').count()

    return render(request, 'admin_panel/orders.html', {
        'orders': orders,
        'pending_count': pending_count,
        'preparing_count': preparing_count,
    })

@login_required
def admin_transactions(request):
    """Display transaction history in admin panel"""
    completed_orders = Order.objects.filter(
        status='completed',
        payment_status='paid'
    ).order_by('-created_at')

    total_revenue = sum(
        order.menu_item.price * order.quantity 
        for order in completed_orders
    )

    return render(request, 'admin_panel/transactions.html', {
        'orders': completed_orders,
        'total_revenue': total_revenue
    })

@login_required
def update_order_status(request, order_id):
    """Update the status of an order"""
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            
            # Try to parse JSON data
            try:
                data = json.loads(request.body)
                new_status = data.get('status')
                kitchen_note = data.get('note', '')
            except json.JSONDecodeError:
                # If not JSON, try form data
                new_status = request.POST.get('status')
                kitchen_note = request.POST.get('note', '')
            
            if not new_status:
                return JsonResponse({'success': False, 'error': 'No status provided'}, status=400)
            
            if new_status in ['pending', 'preparing', 'completed', 'cancelled']:
                order.order_status = new_status
                
                # Record completion time if status is completed
                if new_status == 'completed' and not order.completed_at:
                    order.completed_at = timezone.now()
                
                # Save kitchen note
                if kitchen_note:
                    order.kitchen_notes = kitchen_note
                
                order.save()
                
                # Notify other systems or update related records as needed
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required
def add_menu_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        category = Category.objects.get(id=category_id)
        menu_item = MenuItem.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
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
@login_required
def toggle_table_status(request):
    """Toggles a table's active status."""
    if request.method == "POST":
        data = json.loads(request.body)
        table_number = data.get("table_number")
        try:
            table = Table.objects.get(number=table_number)
            table.is_active = not table.is_active
            table.save()
            return JsonResponse({'success': True})
        except Table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Table not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# --------------------- KITCHEN VIEW ---------------------
def kitchen_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "kitchen/kitchen_login.html")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("kitchen_dashboard")
        else:
            # Check if the username exists
            if User.objects.filter(username=username).exists():
                messages.warning(request, "Username exists, but the password is incorrect.")
            else:
                messages.error(request, f"User '{username}' does not exist in the database.")

    return render(request, "kitchen/kitchen_login.html")


@login_required
def kitchen_dashboard(request):
    # Get pending and preparing orders
    orders = Order.objects.filter(
        order_status__in=['pending', 'preparing']
    ).order_by('-created_at')
    
    # Get statistics
    today = timezone.now().date()
    completed_today = Order.objects.filter(
        order_status='completed',
        completed_at__date=today
    ).count()
    
    pending_count = Order.objects.filter(order_status='pending').count()
    preparing_count = Order.objects.filter(order_status='preparing').count()
    
    # Calculate average preparation time (from order created to completed)
    completed_orders = Order.objects.filter(
        order_status='completed',
        completed_at__isnull=False
    ).order_by('-completed_at')[:50]  # Last 50 completed orders
    
    total_prep_time = 0
    count = 0
    
    for order in completed_orders:
        # Calculate time difference in minutes
        if order.completed_at:
            prep_time = (order.completed_at - order.created_at).total_seconds() / 60
            total_prep_time += prep_time
            count += 1
    
    avg_prep_time = round(total_prep_time / count) if count > 0 else 0
    
    return render(request, "kitchen/kitchen_dashboard.html", {
        'orders': orders,
        'completed_today': completed_today,
        'avg_prep_time': avg_prep_time,
        'pending_count': pending_count,
        'preparing_count': preparing_count
    })

@login_required
def orders_page(request):
    orders = Order.objects.all().order_by('-created_at')
    
    # Get statistics for the dashboard
    pending_count = orders.filter(order_status='pending').count()
    preparing_count = orders.filter(order_status='preparing').count()
    
    # Today's orders
    today = timezone.now().date()
    today_count = orders.filter(created_at__date=today).count()
    
    # Calculate average preparation time (mock data for now)
    avg_prep_time = 15  # In minutes
    
    # Get all tables for the filter dropdown
    tables = Table.objects.all().order_by('number')
    
    return render(request, 'admin_panel/orders.html', {
        'orders': orders,
        'pending_count': pending_count,
        'preparing_count': preparing_count,
        'today_count': today_count,
        'avg_prep_time': avg_prep_time,
        'tables': tables
    })

@login_required
def order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order_details = OrderDetail.objects.filter(order=order)
        payment = Payment.objects.filter(order=order).first()
        
        data = {
            'order': {
                'id': order.id,
                'table': order.table.number if order.table else 'N/A',
                'total_price': str(order.total_price),
                'order_status': order.order_status,
                'payment_status': order.payment_status,
                'created_at': order.created_at.isoformat()
            },
            'order_details': [{
                'menu_name': detail.menu_name,
                'qty': detail.qty,
                'price': str(detail.price),
                'total_price': str(detail.total_price)
            } for detail in order_details],
            'payment': {
                'payment_method': payment.payment_method if payment else None,
                'payment_status': payment.payment_status if payment else None
            } if payment else None
        }
        return JsonResponse(data)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@login_required
def filter_orders(request):
    status = request.GET.get('status', '')
    table = request.GET.get('table', '')
    date = request.GET.get('date', '')
    sort = request.GET.get('sort', 'newest')
    
    orders = Order.objects.all()
    
    if status:
        orders = orders.filter(order_status=status)
    if table:
        orders = orders.filter(table__number=table)
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date=date_obj)
        except ValueError:
            pass
    
    # Sort the orders
    if sort == 'oldest':
        orders = orders.order_by('created_at')
    elif sort == 'table':
        # Use conditionally_sorted to handle None values
        orders = sorted(orders, key=lambda x: (x.table is None, x.table.number if x.table else 0))
    else:  # Default to newest
        orders = orders.order_by('-created_at')
    
    orders_data = [{
        'id': order.id,
        'table': f"Table {order.table.number}" if order.table else 'N/A',
        'total_price': str(order.total_price),
        'order_status': order.order_status,
        'order_status_display': order.get_order_status_display(),
        'created_at': order.created_at.isoformat(),
        'items_count': order.orderdetail_set.count()
    } for order in orders]
    
    return JsonResponse({'orders': orders_data})

@login_required
def transactions_view(request):
    transactions = Payment.objects.all().order_by('-created_at')
    today = timezone.now().date()
    
    # Calculate statistics
    today_revenue = Payment.objects.filter(
        created_at__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('order__total_price'))['total'] or 0
    
    total_transactions = transactions.count()
    successful_transactions = transactions.filter(payment_status='paid').count()
    success_rate = round((successful_transactions / total_transactions * 100) if total_transactions > 0 else 0, 1)
    
    context = {
        'transactions': transactions,
        'today_revenue': today_revenue,
        'total_transactions': total_transactions,
        'success_rate': success_rate
    }
    return render(request, 'admin_panel/transactions.html', context)

@login_required
def transaction_details(request, transaction_id):
    try:
        transaction = Payment.objects.get(id=transaction_id)
        order = transaction.order
        
        data = {
            'transaction': {
                'id': transaction.id,
                'amount': str(order.total_price),
                'payment_status': transaction.payment_status,
                'payment_status_display': transaction.get_payment_status_display(),
                'payment_method': transaction.get_payment_method_display(),
                'created_at': transaction.created_at.isoformat()
            },
            'order': {
                'id': order.id,
                'table': f"Table {order.table.number}",
                'order_status': order.get_order_status_display()
            }
        }
        return JsonResponse(data)
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)

@login_required
def filter_transactions(request):
    transactions = Payment.objects.all()
    
    status = request.GET.get('status')
    method = request.GET.get('method')
    date = request.GET.get('date')
    
    if status:
        transactions = transactions.filter(payment_status=status)
    if method:
        transactions = transactions.filter(payment_method=method)
    if date:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        transactions = transactions.filter(created_at__date=date_obj)
    
    transactions = transactions.order_by('-created_at')
    
    data = {
        'transactions': [{
            'id': t.id,
            'order_id': t.order.id,
            'amount': str(t.order.total_price),
            'payment_method_display': t.get_payment_method_display(),
            'payment_status': t.payment_status,
            'payment_status_display': t.get_payment_status_display(),
            'created_at': t.created_at.isoformat()
        } for t in transactions]
    }
    return JsonResponse(data)