from django.db import models

# Create your models here.

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_date = models.DateField()
    comments = models.TextField(blank=True, null=True)
    products = models.ManyToManyField('Product', through='OrderProduct') 
    completed = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)   

    def __str__(self):
        return self.name

    def get_rest_to_pay(self):
        if self.delivered:
            return 0
        return self.total_amount - self.deposit_amount

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in order {self.order.id}"


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(
        choices=[
            ('buche', 'Buche'),
            ('pain', 'Pain'),
            ('autre', 'Autre'),
            ('patisserie', 'Pâtisserie'),
            ('viennoiserie', 'Viennoiserie'),
            ('galette', 'Galette'),
        ], max_length=20, default='autre'
    )

    def __str__(self):
        return self.name
