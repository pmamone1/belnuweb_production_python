from django.shortcuts import render
from django.core.paginator import Paginator

from store.models import Product, Banner

# Create your views here.

def home(request):
    banner = Banner.objects.filter(is_active=True)
    products = Product.objects.all().filter(is_available=True)
    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()
    primer_banner = banner.last()
    context = {'products':paged_products,
               'product_count': product_count,
               'banner': banner,
               'primer_banner': primer_banner,
               }
    #print(banner)
    return render(request, 'home.html', context)

