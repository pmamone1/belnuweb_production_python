from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('el usuario debe tener un email')

        if not username:
            raise ValueError('el usuario debe tener un username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user





class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50,verbose_name='Nombre')
    last_name = models.CharField(max_length=50,verbose_name='Apellido')
    username = models.CharField(max_length=50, unique=True,verbose_name='Usuario')
    email = models.CharField(max_length=100, unique=True,verbose_name='Email')
    phone_number = models.CharField(max_length=50,verbose_name='Telefono',blank=True)

    #campos atributos de django
    date_joined = models.DateTimeField(auto_now_add=True,verbose_name='Fecha de registro')
    last_login = models.DateTimeField(auto_now_add=True,verbose_name='Ultimo login')
    is_admin = models.BooleanField(default=False,verbose_name='Administrador')
    is_staff = models.BooleanField(default=False,verbose_name='Staff')
    is_active = models.BooleanField(default=False,verbose_name='Activo')
    is_superadmin = models.BooleanField(default=False,verbose_name='Superadmin')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()
    class Meta:
        verbose_name = "Cuenta de Usuario"
        verbose_name_plural = "Cuentas de Usuarios"
        ordering = ['date_joined']
        
   
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE,verbose_name='Usuario')
    address_line_1 =  models.CharField(blank=True, max_length=100,verbose_name='Dirección')
    address_line_2 =  models.CharField(blank=True, max_length=100,verbose_name='Dirección 2')
    profile_picture = models.ImageField(blank=True, upload_to='userprofile',verbose_name='Imagen de Perfil')
    city = models.CharField(blank=True, max_length=20,verbose_name='Ciudad')
    state = models.CharField(blank=True, max_length=20,verbose_name='Provincia')
    country = models.CharField(blank=True, max_length=20,verbose_name='Pais')
    numero_vendedor = models.IntegerField(blank=True,verbose_name='Numero de vendedor',unique=True,null=True)
    nombre_vendedor = models.CharField(blank=True,max_length=15,verbose_name='Nombre de vendedor',unique=True,null=True)
    
    def __str__(self):
        return self.full_name() + ' - ' + str(self.numero_vendedor) + ' - ' + self.nombre_vendedor
    
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def full_name(self):
        return f'{self.user.full_name()}'

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"


class Subcuenta(models.Model):
    nombre = models.CharField(max_length=50,verbose_name='Nombre',unique=True)
    codigo =models.CharField(max_length=50,verbose_name='Codigo',unique=True)
    provincia = models.CharField(max_length=50,verbose_name='Provincia')
    ciudad = models.CharField(max_length=50,verbose_name='Ciudad')
    observaciones = models.CharField(max_length=250,verbose_name='Observaciones',blank=True)
    distribuidora = models.ForeignKey('Distribuidora',on_delete=models.CASCADE,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Fecha de creacion')
    updated_at = models.DateTimeField(auto_now=True,verbose_name='Fecha de actualizacion')
    
    def __str__(self):
        return self.nombre + ' ' + self.codigo

class Distribuidora(models.Model):
    nombre = models.CharField(max_length=50,verbose_name='Nombre Distribuidora')
    codigo = models.CharField(max_length=50,verbose_name='Codigo Distribuidora')
    provincia = models.CharField(max_length=50,verbose_name='Provincia')
    ciudad = models.CharField(max_length=50,verbose_name='Ciudad')
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Fecha de creacion')
    updated_at = models.DateTimeField(auto_now=True,verbose_name='Fecha de actualizacion')
    
    def __str__(self):
        return self.codigo + " - " + self.nombre
