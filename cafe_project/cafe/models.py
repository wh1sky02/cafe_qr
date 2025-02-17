from django.db import models

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
    name = models.CharField(max_length=100, null=True, blank=True)
    capacity = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.number} ({self.name})"


# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)