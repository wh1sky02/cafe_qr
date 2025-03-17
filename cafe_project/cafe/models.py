from django.db import models
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
    class Status(models.TextChoices):
        REGULAR = 'regular', 'Regular'
        SET_MENU = 'set_menu', 'Set Menu'

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.REGULAR)
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

    def __str__(self):
        return f"Table {self.number}"

class QRCode(models.Model):
    table = models.OneToOneField(Table, on_delete=models.CASCADE, related_name='qr_code')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_qr_code(self):
        url = f'http://localhost:8000/menu/{self.token}/'
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
        self.qr_code.save(f'table_{self.token}_qr.png', File(buffer), save=False)
        self.save()

    def get_qr_code_url(self):
        return self.qr_code.url if self.qr_code else None
    
    def __str__(self):
        return f"QR Code for Table {self.table.number}"

class OrderSession(models.Model): 
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="order_sessions")
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    test_field = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"Session {self.session_id} for Table {self.table.number}"

    @classmethod
    def get_active_session(cls, table):
        session = cls.objects.filter(table=table, is_active=True).order_by("-created_at").first()
        return session if session else cls.objects.create(table=table)

class Order(models.Model):
    session = models.ForeignKey(
        OrderSession, 
        on_delete=models.CASCADE, 
        related_name="orders",
        null=True,  # Allows NULL values
        blank=True  # Allows empty values in forms
    )
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.session.session_id} - {self.quantity}x {self.menu_item.name}"

    def mark_as_completed(self):
        self.is_completed = True
        self.save()
    
class Banner(models.Model):
    image = models.ImageField(upload_to='banners/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Banner {self.id}"