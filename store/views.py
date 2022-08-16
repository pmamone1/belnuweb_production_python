from logging import exception
from django.shortcuts import render, get_object_or_404, redirect,HttpResponse,HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from rest_framework import viewsets
from .serializers import VariationSerializer
import json
from store.forms import ProductForm
from store.models import ProductGallery

from carts.models import CartItem
from carts.views import _cart_id
from .forms import ReviewForm
from .models import Product, Variation,ReviewRating,Banner
from category.models import Category
from orders.models import OrderProduct

def store(request, category_slug=None):
    banner = Banner.objects.filter(is_active=True)
    categories = None
    products = None
    category = Category.objects.all()
        

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    
    context =  {
        'products' : paged_products,
        'product_count': product_count,
        'category': category,
        'banner': banner,        
    }

    return render(request, 'store/store.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
            
        except orderproduct.DoesNotExist:
            orderproduct = None
        
        product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
        context = {
            'single_product': single_product,
            'in_cart': in_cart,
            'orderproduct': orderproduct,
            'product_gallery': product_gallery,
        }
    except Exception as e:
        raise e
            
    return render(request, 'store/product_detail.html', context)

def product_detail_2(request, category_slug, product_slug,edicion):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        edicion= Variation.objects.get(variation_value=edicion, product=single_product)
        precio_ed = edicion.precio_ed
        if precio_ed == None:
            precio_ed = single_product.price
        
        product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
        
        context = {
            'single_product': single_product,
            'in_cart': in_cart,
            'edicion': edicion,
            'precio_ed': precio_ed,
            'product_gallery': product_gallery,
        }
    except Exception as e:
        raise e
            
    return render(request, 'store/product_detail.html', context)

def get_ajax_titulo(request):
    print("serializer data")
    titulo=request.GET.get('titulo')
    edicion=request.GET.get('edicion')
    print(titulo,edicion)        
        
    variations = Variation.objects.get(variation_value=edicion, product=titulo)
    serializer = VariationSerializer(variations)
    print("Pablo...",serializer.data)
    #return HttpResponse(serializer.data)
    return HttpResponse(json.dumps({"data":serializer.data}), content_type="application/json")
  
def nuevo_producto(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente!')
            return redirect('store')
    else:
        form = ProductForm()
    return render(request, 'store/nuevo_producto.html', {'form': form})

def submit_review(request, product_id):
    print("El product id es="+ str(product_id))
    url = request.META.get('HTTP_REFERER') # get url of previous page
    
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form = ReviewForm(request.POST,instance=reviews)
            if form.is_valid():
                form.save()
                messages.success(request, 'Se guardo tu comentario!')
                return redirect(url)
            else:
                messages.warning(request, 'Faltan completar campos!')
                return redirect(url)            
        except ReviewRating.DoesNotExist:
            form=ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR') # get ip address of user
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Se guardo tu comentario!')
                return redirect(url)
            else:
                messages.warning(request, 'Faltan completar campos!')
                return redirect(url)            
                