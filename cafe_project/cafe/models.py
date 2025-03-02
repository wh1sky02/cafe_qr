from django.db import models
from django.utils.timezone import now
import qrcode
import uuid
from io import BytesIO
from django.core.files import File
from PIL import Image
from io import BytesIO

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
    created_at = models.DateTimeField(auto_now_add=True)  # For determining "new" items

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            output_size = (96, 96)
            img.thumbnail(output_size, Image.LANCZOS)
            # Save the resized image
            thumb_io = BytesIO()
            img.save(thumb_io, img.format, quality=85)
            self.image.file = thumb_io
            self.image.name = self.image.name
        super().save(*args, **kwargs)
    
class Table(models.Model):
    number = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    def __str__(self):
        return f"Table {self.number}"

    def generate_qr_code(self):
        # Generate the URL for this table's menu based on the token
        url = f'http://localhost:8000/menu/{self.token}/'

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # qr.add_data(f'http://cafe101.store/menu/{self.number}/')
        qr.add_data(url)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save QR code image
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        self.qr_code.save(f'table_{self.token}_qr.png', File(buffer), save=False)
        self.save()  # Save the table with the QR code image

    def get_qr_code_url(self):
        if self.qr_code:
            return self.qr_code.url  # Return the URL of the generated QR code image
        return None

class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="orders")  
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Table {self.table.number} - {self.quantity}x {self.menu_item.name}"
    
class Banner(models.Model):
    image = models.ImageField(upload_to='banners/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Banner {self.id} - {'Active' if self.is_active else 'Inactive'}"  