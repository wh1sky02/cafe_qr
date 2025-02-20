from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

# Create your models here.
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    is_bestseller = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Table(models.Model):
    number = models.IntegerField(unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # Generate unique URL for this table
        qr.add_data(f'http://yourcafe.com/menu/{self.number}/')
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code image
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        self.qr_code.save(f'table_{self.number}_qr.png', File(buffer), save=False)


# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)