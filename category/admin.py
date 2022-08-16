from django.contrib import admin
from .models import Category
from django.utils.html import format_html

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name','slug','imagen')
    
    def imagen(self,obj):
        return format_html('<img src={}  width="80px" height="80px" />',obj.cat_image.url)
    
# Register your models here.
admin.site.register(Category,CategoryAdmin)

