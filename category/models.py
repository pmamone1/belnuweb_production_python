from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50,unique=True,verbose_name='Categoria')
    description = models.CharField(max_length=255,blank=True,verbose_name='Descripcción')
    slug = models.SlugField(max_length=100,unique=True)
    cat_image = models.ImageField(upload_to='photos/categories',blank=True,verbose_name='Imagen')
    
    
    def get_url(self):
        return reverse('product_by_category',args=[self.slug])
    
    
    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        