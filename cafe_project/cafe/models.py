
from django.db import models
import uuid
from django.utils.timezone import now
import qrcode
import uuid
from io import BytesIO
from django.core.files import File
from PIL import Image

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
            output_size = (96, 96)
            img.thumbnail(output_size, Image.LANCZOS)
            thumb_io = BytesIO()
            img.save(thumb_io, img.format, quality=85)
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

class Order(models.Model):
    session = models.ForeignKey(OrderSession, on_delete=models.CASCADE, related_name='orders', null=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.menu_item.name} x{self.quantity}"

class Banner(models.Model):
    image = models.ImageField(upload_to='banners/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Banner {self.id}"
