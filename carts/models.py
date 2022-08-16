from django.db import models
from store.models import Product, Variation
from accounts.models import Account, UserProfile
# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True,verbose_name="Carrito de compras")
    date_added = models.DateField(auto_now_add=True,verbose_name='Fecha de registro')

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE,null=True,verbose_name='Usuario')
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE,null=True,blank=True,verbose_name='Perfil de usuario')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,verbose_name='Producto')
    variations = models.ManyToManyField(Variation, blank=True,verbose_name='Edicion')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True,verbose_name='Carro')
    quantity = models.IntegerField(verbose_name='Cantidad')
    is_active = models.BooleanField(default=True,verbose_name='Activo')

    
    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product.product_name
