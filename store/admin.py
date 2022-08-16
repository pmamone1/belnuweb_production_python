from django.contrib import admin
from .models import Product,Variation,Banner,ReviewRating,ProductGallery

from django.utils.html import format_html
import admin_thumbnails


# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','description', 'price', 'recargo_interior', 'porcentaje_vv','stock','category', 'is_available','imagen')
    list_filter = ('is_available', 'category', 'modified_date')
    search_fields = ('product_name',)
    prepopulated_fields = {'slug': ('product_name',)}

    inlines = [ProductGalleryInline]
    
    def imagen(self,obj):
        return format_html('<img src={}  width="80px" height="80px" />',obj.images.url)

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','subtitulo','variation_value','stock','precio_ed','is_active','imagen','image')
    list_editable = ("stock","subtitulo","precio_ed","is_active","image",)
    search_fields = ['product__product_name','subtitulo','is_active','variation_value','stock']
    list_filter = ['product','is_active']
    autocomplete_fields = ['product']
    
    def imagen(self,obj):
        if obj.image:
            return format_html('<img src={}  width="80px" height="80px" />',obj.image.url)

class BannerAdmin(admin.ModelAdmin):
    list_display = ('coleccion','image','date_created','proveedor','is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'proveedor')

class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product','rating')



admin.site.register(Product, ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(Banner,BannerAdmin)
admin.site.register(ReviewRating,ReviewRatingAdmin)


