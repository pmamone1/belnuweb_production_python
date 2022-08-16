from tabnanny import verbose
from django.db import models
from category.models import Category
from accounts.models import Account
from django.db.models import Avg, Count
from django.urls import reverse
import computed_property


# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True,verbose_name='Nombre Producto')
    slug = models.SlugField(max_length=200)
    description = models.CharField(max_length=500,blank=True,verbose_name='Descripción',null=True)
    price = models.DecimalField(max_digits=18,decimal_places=2,verbose_name='PVP')
    recargo_interior = models.DecimalField(max_digits=18,decimal_places=2,verbose_name='Recargo Interior')
    porcentaje_vv = models.DecimalField(max_digits=18,decimal_places=2,verbose_name='% Vendedor')
    images = models.ImageField(upload_to='photos/products',verbose_name='Imagen')
    #stock = computed_property.ComputedIntegerField(compute_from='stock_total',verbose_name="Stock")
    stock_p=models.IntegerField(verbose_name="Stock_p",default=1)
    is_available = models.BooleanField(default=True,verbose_name='Disponible')
    category = models.ForeignKey(Category,on_delete=models.CASCADE,verbose_name='Categoria')
    created_date = models.DateField(auto_now_add=True,verbose_name='Fecha de creacion')
    modified_date = models.DateField(auto_now=True,verbose_name='Fecha de actualizacion')
    

        
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['product_name', '-created_date']
    
    
    def __str__(self):
        return self.product_name
    
    def get_url(self):
        try:
            return reverse('product_detail', args=[self.category.slug, self.slug])
        except:
            pass
        
    @property    
    def stock(self,stock=0):
        ediciones = Variation.objects.filter(product=self.id)        
        print(ediciones.count())
        print(ediciones)
        i=0
        for x in ediciones:
            i +=1
            print("titulo: ", str(x.id))
            print("titulo", x.product.product_name)
            print("edicion: ", x.variation_value)
            print("el stock es "+ str(x.stock))
                
            stock += x.stock
            print("stock parcial:"+str(stock))
            print(i)
        if stock is not None:
            print("el stock total seria="+str(stock))
            return stock      
        class Meta:
            verbose_name = "Stock"   
        

    @property
    def pvp_total(self):
        try:
            return self.price + self.recargo_interior
        except:
            pass
        
    @property
    def precio_vv(self):
        try:
            return (self.price*self.porcentaje_vv/100) + self.recargo_interior
        except:
            pass
        
    @property
    def averageReview(self):
        try:
            reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
            avg=0
            if reviews['average'] is not None:
                avg = float(reviews['average'])
            return avg
        except:
            pass
        
    @property
    def countReview(self):
        try:
            reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
            count=0
            if reviews['count'] is not None:
                count = int(reviews['count'])

            return count
        except:
            pass
 
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.CharField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Valoracion"
        verbose_name_plural = "Valoraciones"
        ordering = ['rating']
    
    def __str__(self):
        return self.subject

variation_category_choices = (
                                ('Edicion', 'Edicion'),
                            )

class VariationManager(models.Manager):
    def edicion(self):
        return super(VariationManager, self).filter(variation_category="Edicion",is_active=True)
    


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,verbose_name='Producto',null=True)
    subtitulo = models.CharField(max_length=100,verbose_name='Subtitulo',blank=True)
    variation_category = models.CharField(max_length=200,verbose_name='Variacion', choices = variation_category_choices,default='Edicion')
    variation_value = models.CharField(max_length=200,verbose_name='Edicion')
    stock = models.IntegerField(verbose_name='Stock')
    image = models.ImageField(upload_to='photos/products',blank=True,verbose_name='URL_Imagen',null=True)
    is_active = models.BooleanField(default=True,verbose_name='Disponible')
    created_date = models.DateField(auto_now_add=True,verbose_name='Fecha de creacion')
    updated_date = models.DateField(auto_now=True,verbose_name='Fecha de actualizacion')
    precio_ed = models.DecimalField(max_digits=18,decimal_places=2,verbose_name='Precio Ed.',null=True,blank=True)
    
    objects = VariationManager()
    
    def get_url_2(self):
        return reverse('product_detail_2', args=[self.product.category.slug, self.product.slug,self.variation_value])
    
    def __str__(self):
        return self.variation_category + ": " + self.variation_value
    
    
    
    class Meta:
        verbose_name = "Edicion"
        verbose_name_plural = "Ediciones"
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'variation_value'], name='id_titulo_edicion'
            )
        ]       

class Banner(models.Model):
    Proveedor=(
        ('Clarin','Clarin'),
        ('La Nacion','La Nacion'),
        ('Planeta','Planeta'),
        ('Salvat','Salvat'),
        ('Perfil','Perfil'),
        ('Otro','Otro'),
    )

    
    coleccion = models.CharField(max_length=100,verbose_name='Coleccion')
    image = models.ImageField(upload_to='photos/banners',verbose_name='URL_Imagen')
    proveedor = models.CharField(max_length=100,verbose_name='Proveedor',blank=True,null=True,choices=Proveedor)
    is_active = models.BooleanField(default=True,verbose_name='Activo')
    date_created = models.DateField(auto_now_add=True,verbose_name='Fecha de creacion',blank=True,null=True)
    
    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,verbose_name='Producto',default=None)
    image = models.ImageField(upload_to='store/products',max_length=255,verbose_name='Imagenes')
    
    def __str__(self):
        return self.product.product_name
    