from django.contrib import admin
from .models import Order, OrderProduct
from import_export.admin import ExportActionMixin

# Register your models here.

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['created_at','numero_pedido', 'product', 'quantity','product_price','ordered']

class OrderProductInline(ExportActionMixin,admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product', 'quantity', 'product_price','ordered','created_at')
    extra = 0

class OrderAdmin(ExportActionMixin,admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email','status','is_ordered','created_at']
    readonly_fields =('order_total',)
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number','first_name','last_name','phone','email']
    list_per_page = 20
    
    inlines = [OrderProductInline]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct,OrderProductAdmin)
