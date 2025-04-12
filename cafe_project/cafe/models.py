from django.db import models
import uuid
from django.utils.timezone import now
import qrcode
import uuid
from io import BytesIO
from django.core.files import File
from PIL import Image
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            output_size = (400, 400)  # Increased size for better quality
            img.thumbnail(output_size, Image.LANCZOS)
            thumb_io = BytesIO()
            img.save(thumb_io, img.format, quality=95)  # Increased quality
            self.image.file = thumb_io
            self.image.name = self.image.name
        super().save(*args, **kwargs)

class Table(models.Model):
    number = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    token = models.UUIDField(null=True, blank=True)
    
    def __str__(self):
        return f"Table {self.number}"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4()
        super().save(*args, **kwargs)

class QRCode(models.Model):
    table = models.OneToOneField(Table, on_delete=models.CASCADE, related_name='qr_code')
    token = models.UUIDField(editable=False, unique=True)
    image = models.ImageField(upload_to='qr_codes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR Code for Table {self.table.number}"
        
    def generate_token(self):
        # Generate token using table number and UUID
        return uuid.uuid5(uuid.NAMESPACE_DNS, f"table_{self.table.number}")
        
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)

    def generate_qr_code(self):
        url = f'http://localhost:8000/menu/{self.table.token}/'
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        self.image.save(f'{self.table.token}_{self.token}.png', File(buffer), save=False)

class OrderSession(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Session for Table {self.table.number}"

class Banner(models.Model):
    image = models.ImageField(upload_to='banners/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Banner {self.id}"

class Cart(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    menu_name = models.CharField(max_length=100)
    image = models.CharField(max_length=255)
    qty = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = self.qty * self.price
        super().save(*args, **kwargs)

class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed')
    ], default='pending')
    kitchen_notes = models.TextField(blank=True, null=True, help_text="Notes from kitchen staff about the order")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When the order was marked as completed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.get_order_status_display()}"
        
    def get_preparation_time(self):
        """Returns the preparation time in minutes"""
        if self.completed_at and self.order_status == 'completed':
            time_diff = self.completed_at - self.created_at
            return round(time_diff.total_seconds() / 60)
        return None

    @classmethod
    def get_pending_orders(cls):
        """Returns all pending orders."""
        return cls.objects.filter(order_status='pending')

    @classmethod
    def get_preparing_orders(cls):
        """Returns all preparing orders."""
        return cls.objects.filter(order_status='preparing')

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_name = models.CharField(max_length=100)
    image = models.CharField(max_length=255)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, default='')
    table_number = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.qty * self.price
        self.gst_amount = self.subtotal * Decimal('0.09')
        self.total_price = self.subtotal + self.gst_amount + self.tip_amount
        
        # Save the table number if it's not already set and the order has a table
        if not self.table_number and self.order_id and self.order.table:
            self.table_number = self.order.table.number
            
        super().save(*args, **kwargs)

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'Cash'),
        ('card', 'Card')
    ])
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
