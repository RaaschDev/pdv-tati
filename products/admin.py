from django.contrib import admin
from .models import Category, Product, Tables, Order, OrderItem
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Tables)



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    def close_order(self, request, queryset):
        for order in queryset:
            order.status = 'closed'
            order.save()

    close_order.short_description = 'Fechar Pedido'

    actions = [close_order]
