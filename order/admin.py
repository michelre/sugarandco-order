from django.contrib import admin
from .models import Order, OrderProduct, Product

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    autocomplete_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'total_amount', 'deposit_amount', 'delivery_date', 'created_at')
    list_filter = ('delivery_date', 'created_at')
    search_fields = ('name', 'phone', 'comments')
    inlines = [OrderProductInline]
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__name', 'product__name')
