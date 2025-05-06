from django.db import models
from utils.models.base_model import BaseModel
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

class Stock(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Nome")
    quantity = models.IntegerField(verbose_name="Quantidade")

    class Meta:
        verbose_name = "Estoque"
        verbose_name_plural = "Estoque"


class Category(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Nome")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name
    
class Product(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Nome")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Categoria")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.name


class Tables(BaseModel):
    status_choices = [
        ("disponivel", "Disponível"),
        ("ocupado", "Ocupado"),
        ("reservado", "Reservado"),
    ]

    number = models.IntegerField(verbose_name="Número")
    chairs = models.IntegerField(verbose_name="Cadeiras")
    status = models.CharField(max_length=255, choices=status_choices, verbose_name="Status", default="disponivel")

    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ['number']

    def __str__(self):
        return f"Mesa {self.number}"


class Order(BaseModel):
    table = models.ForeignKey(Tables, on_delete=models.CASCADE, verbose_name="Mesa", related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Total", default=0)
    status_choices = [
        ("aberto", "Aberto"),
        ("fechado", "Fechado"),
    ]
    status = models.CharField(max_length=255, choices=status_choices, verbose_name="Status", default="aberto")
    payment_method_choices = [
        ("dinheiro", "Dinheiro"),
        ("cartao", "Cartão"),
        ("pix", "PIX"),
    ]
    payment_method = models.CharField(max_length=255, choices=payment_method_choices, verbose_name="Forma de Pagamento", null=True, blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido {self.id}"




class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Pedido", related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produto")
    quantity = models.IntegerField(verbose_name="Quantidade")
    total_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor", blank=True, null=True, default=0)

    class Meta:
        verbose_name = "Item do pedido"
        verbose_name_plural = "Itens do pedido"

    def __str__(self):
        return f"Item do pedido {self.id}"
    

@receiver(pre_save, sender=OrderItem)
def calculate_item_value(sender, instance, **kwargs):
    if instance.product and instance.quantity:
        instance.total_value = instance.product.price * instance.quantity


@receiver(post_save, sender=OrderItem)
def calculate_order_total(sender, instance, **kwargs):
    order = instance.order
    order_items = OrderItem.objects.filter(order=order)
    total = sum(item.product.price * item.quantity for item in order_items)
    order.total_price = total
    order.save()


@receiver(post_save, sender=Order)
def update_table_status(sender, instance, **kwargs):
    if instance.table.status == "disponivel":
        instance.table.status = "ocupado"
        instance.table.save()
