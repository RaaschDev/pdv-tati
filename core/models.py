from django.db import models
from products.models import Product, Tables, OrderItem
# Create your models here.

class FinishedOrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class FinishedOrder(models.Model):
    PAYMENT_METHODS = [
        ("dinheiro", "Dinheiro"),
        ("cartao", "Cartão"),
        ("pix", "PIX"),
    ]

    table = models.ForeignKey(Tables, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(FinishedOrderItem)

    def __str__(self):
        return f"Pedido finalizado - Mesa {self.table.number} - {self.created_at}"
