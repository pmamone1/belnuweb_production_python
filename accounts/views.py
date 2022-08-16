from datetime import datetime
from telnetlib import STATUS
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserProfileForm, UserForm
from .models import Account, UserProfile
from orders.models import Order, OrderProduct
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models import Q
from .serializers import OrderSerializer
#from django.shortcuts import HttpResponse
from django.http import HttpResponse 
import json
import xlwt

import smtplib
import ssl
from email.message import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests

import environ
env = environ.Env()
environ.Env.read_env()

PASSWORD_GMAIL = env('PASSWORD_GMAIL')


# Create your views here.
def register(request):
    form = RegistrationForm()
    
    if request.method == 'POST':
        numero_vendedor = request.POST.get('numero_vendedor',"")
        nombre_vendedor = request.POST.get('nombre_vendedor',"")
        if numero_vendedor == "" or nombre_vendedor == "":
            messages.warning(request, 'No ingreso Numero y/o Nombre de Vendedor')
            return redirect('register')             
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password )
            user.phone_number = phone_number
            user.save()


            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.numero_vendedor = numero_vendedor
            profile.nombre_vendedor = nombre_vendedor
            profile.save()

            current_site = get_current_site(request)

            # Configuracion de los mails
            email_sender = 'belnu.pedidos@gmail.com'
            email_password = env('PASSWORD_GMAIL') #esta es la contraseña global de gmail para este mail
            email_receiver = email

            # configuramos el mail 
            subject = 'Por favor activa tu cuenta en Belnu Pedidos Web!'
            body = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)

            # Add SSL (layer of security)
            context = ssl.create_default_context()

            # Log in and send the email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
                messages.success(request, 'Se registro el usuario exitosamente')
            return redirect('/accounts/login/?command=verification&email='+email)


    context = {
        'form': form
    }

    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        print("El user es =", user)
        if user is not None:
            print("hay usu")
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation= item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    #  product_variation = [1, 2, 3, 4, 5]
                    #  ex_var_list = [5, 6, 7, 8]

                    for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity +=1
                                item.user = user
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()
            except:
                pass


            # http://127.0.0.1:8000/accounts/login/?next=/cart/checkout/
            
            auth.login(request, user)
            messages.success(request, 'Has iniciado sesion exitosamente')
            url  = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
    
        else:
            
            if Account.objects.filter(email=email).exists():
                user=Account.objects.filter(email=email).first()
                print("pppp" +email)
                messages.error(request, 'El usuario no se encuentra activo')
                current_site = get_current_site(request)

                # Configuracion de los mails
                email_sender = 'belnu.pedidos@gmail.com'
                email_password = env('PASSWORD_GMAIL') #esta es la contraseña global de gmail para este mail
                email_receiver = email

                # configuramos el mail 
                subject = 'Por favor activa tu cuenta en Belnu Pedidos Web!'
                body = render_to_string('accounts/account_verification_email.html', {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['Subject'] = subject
                em.set_content(body)

                # Add SSL (layer of security)
                context = ssl.create_default_context()

                # Log in and send the email
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, email_receiver, em.as_string())
                    messages.success(request, 'No has activado tu cuenta todavia, te hemos enviado un nuevo enlace a tu mail para que puedas activar tu cuenta')
                return redirect('/accounts/login/?command=verification&email='+email)
            else:    
                print("no hay usu")
                messages.error(request, 'Las credenciales son incorrectas')
                return redirect('login')


    return render(request, 'accounts/login.html')
  
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Has salido de sesion')

    return redirect('login')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Felicidades, tu cuenta esta activa!')
        return redirect('login')
    else:
        messages.error(request, 'La activacion es invalida')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    if not request.user.is_admin:
        orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True,status="Accepted")
    else:
        orders = Order.objects.order_by('-created_at').filter(is_ordered=True,status="Accepted")
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
        'users':request.user,
    }

    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)

            # Configuracion de los mails
            email_sender = 'belnu.pedidos@gmail.com'
            email_password = env('PASSWORD_GMAIL') #esta es la contraseña global de gmail para este mail
            email_receiver = email

            # configuramos el mail 
            subject = 'Por favor activa tu cuenta en Belnu Pedidos Web!'
            body = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)

            # Add SSL (layer of security)
            context = ssl.create_default_context()

            # Log in and send the email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
                
            messages.success(request, 'Un email fue enviado a tu bandeja de entrada para resetear tu password')
            return redirect('login')
        else:
            messages.error(request, 'La cuenta de usuario no existe')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user=None

        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = uid
            messages.success(request, 'Por favor resetea tu password')
            return redirect('resetPassword')
        else:
            messages.error(request, 'El link ha expirado')
            return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'El password se reseteo correctamente')
            return redirect('login')
        else:
            messages.error(request, 'El password de confirmacion no concuerda')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')

def filtrar_pedido(request,filtro="1"):
    if request.POST:
        filtro= request.POST.get('filtro')
    #print("*******POST***********"+str(filtro))
    
    
    print("*******GET***********"+str(filtro))
    if filtro==None:
        filtro="1"
        print("Filtro hardcodeado: "+str(filtro))
    print(request.user)
    profile=UserProfile.objects.get(user_id=request.user.id)
    if not request.user.is_admin:
        print("no es admin")
        try:    
            if filtro =="1":
                orders = Order.objects.filter(user=request.user).order_by('-created_at')
            elif filtro =="2":
                orders = Order.objects.filter(user=request.user,is_ordered=True,status="Accepted").order_by('-created_at')
            elif filtro =="3":
                orders = Order.objects.filter(user=request.user,is_ordered=True,status="Completed").order_by('-created_at')
            elif filtro =="4":
                orders = Order.objects.filter(user=request.user,is_ordered=False,status="Cancelado").order_by('-created_at')
            
        except:
            print("hay un error")
            pass
    else:
        print("es admin")
        try:    
            if filtro =="1":
                orders = Order.objects.all().order_by('-created_at')
            elif filtro =="2":
                orders = Order.objects.filter(is_ordered=True,status="Accepted").order_by('-created_at')
            elif filtro =="3":
                orders = Order.objects.filter(is_ordered=True,status="Completed").order_by('-created_at')
            elif filtro =="4":
                orders = Order.objects.filter(is_ordered=False,status="Cancelado").order_by('-created_at')
            
        except:
            print("Hay un error")
            pass
    page = request.GET.get('page')
    print("filtro? "+str(filtro))
    print("pagina? " + str(page))
    
    paginator = Paginator(orders, 5)
    paged_products = paginator.get_page(page)
    product_count = orders.count()
    
    if filtro=="1":
        filtro="Todos"
    elif filtro=="2":
        filtro="Pendientes"
    elif filtro=="3":
        filtro="Completados"
    elif filtro=="4":
        filtro="Cancelados"
    print("el filtro que esta pasando es =" +filtro)
    
    context = {
            'product_count': product_count,
            'orders': paged_products,
            'filtro': filtro,
            'user': profile,
            'users':request.user,
        }
     
    return render(request, 'accounts/my_orders.html', context)
    

def my_orders(request):
    if not request.user.is_admin:
        orders = Order.objects.filter(user=request.user, is_ordered=True,status="Accepted").order_by('-created_at')
    else:
        orders = Order.objects.all().filter(status="Accepted").order_by('-created_at')
        
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = orders.count()
    profile=UserProfile.objects.get(user_id=request.user.id)
    
    context = {
        'product_count': product_count,
        'orders': paged_products,
        'users':request.user,
        'user': profile,
    }
     
    return render(request, 'accounts/my_orders.html', context)

def borrar_pedido(request, pk):
    order = Order.objects.get(pk=pk)
    if order.status =="Accepted":
        print("Entro a borrar pedido!")
        order.status ="Cancelado"
        order.is_ordered = False
        order.save()
        messages.success(request, 'El pedido se cancelo correctamente, se enviara un email al vendedor')
        current_site = get_current_site(request)

        # Configuracion de los mails
        email_sender = 'belnu.pedidos@gmail.com'
        email_password = env('PASSWORD_GMAIL') #esta es la contraseña global de gmail para este mail
        email_receiver = order.email

        # configuramos el mail 
        subject = 'Tu pedido fue Cancelado!'
        body = render_to_string('accounts/borrar_pedido_email.html', {
                'user': order.user,
                'domain': current_site,
                'order':order,
            })

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        # Add SSL (layer of security)
        context = ssl.create_default_context()

        # Log in and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        return redirect('my_orders')
    else:
        messages.error(request, 'El pedido no se pudo cancelar reintentelo!')
        print("no entro a borrar pedido")
        return redirect('my_orders')



@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    vendedor=UserProfile.objects.get(user=request.user)

    print(vendedor.numero_vendedor, vendedor.nombre_vendedor)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Su informacion fue guardada con exito')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
        'numero_vendedor': vendedor.numero_vendedor,
        'nombre_vendedor': vendedor.nombre_vendedor,
        'users':request.user,
    }

    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()

                messages.success(request, 'El Password se actualizo exitosamente')
                return redirect('change_password')
            else:
                messages.error(request, 'Por favor ingrese un password valido')
                return redirect('change_password')
        else:
            messages.error(request, 'El password no coincide con la confirmacion de password')
            return redirect('change_password')
    context={
            'users':request.user,
    }
    return render(request, 'accounts/change_password.html',context)

def selected_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order_product_id = OrderProduct.objects.filter(order=order)

    paginator = Paginator(order_product_id, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = order_product_id.count()
    
    context = {
        'order': order,
        'order_product': paged_products,
        'product_count': product_count,
        'order_p': paged_products,    
        'fecha': order.created_at,
        }
    return render(request, 'accounts/selected_order.html', context)



def cumplir_pedidos(request):
    print("entro a cumplir pedidos")
    messages.success(request, 'Se exporto a excel los pedidos!')
    order = Order.objects.filter(status="Accepted")
    for item in order:
        item.status = "Completed"
        item.save()
    
    return redirect('my_orders')
    


def exporta_pedidos_xls(request):
    messages.success(request, 'Se exporto a excel los pedidos!')
    print("entro al exportador de peidos al excel")
    response = HttpResponse(content_type='application/ms-excel')
    
    response['Content-Disposition'] = 'attachment; filename="Pedidos.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Pedidos')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.easyxf("pattern: pattern solid, fore_color black; font: color white; align: horiz center; border: left thick, top thick, bottom thick, right thick")
    font_style.font.bold = True

    columns = ['Vendedor','Nombre Vendedor','Producto','Edicion','Cantidad','# Pedido', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    order=Order.objects.filter(status="Accepted")
    if order.count() > 0:
        for item in order:
            rows = OrderProduct.objects.filter(order=item).values_list('profile__numero_vendedor', 'profile__nombre_vendedor', 'product__product_name', 'variation__variation_value', 'quantity', 'numero_pedido')
            for row in rows:
                print(row)
                row_num += 1
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; border: left thin, bottom thin, right thin"))

        # Darle estilo al archivo XLS
        estilo = xlwt.XFStyle()
        estilo.alignment.horz = 'HORZ_CENTER'  
        
        bordes = estilo.borders
        estilo.pattern_back_colour = 41
        
        wb.save(response)
        print(response)
        print("se guardo el archivo!")
        
        order = Order.objects.filter(status="Accepted")
        for item in order:
            item.status = "Completed"
            item.save()
        
        return response
    else:
        print("No hay pedidos para exportar")
        messages.error(request, 'No hay pedidos para exportar!')        
