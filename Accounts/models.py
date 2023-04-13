import datetime
import os
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from .models import * 
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
   

    def _create_user(self, email, password=None, **extra_fields):
        
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    mobile = models.CharField(max_length=20)
    mobile_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()



def getFileName(request,filename):
    now_time = datetime.datetime.now().strftime("%Y%m%d%H:%M:%S")
    new_filename = "%s%s"%(now_time,filename)
    return os.path.join('uploads/',new_filename)



class Category(models.Model):
    name = models.CharField(max_length=200,null=False,blank=False)
    image = models.ImageField(upload_to=getFileName,null=True,blank=True)
    description = models.TextField(max_length=500,null=False,blank=False)
    status = models.BooleanField(default=False,help_text="0-show,1-Hidden")
    created_at = models.DateField(auto_now_add=True)
    delete_category = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    


class Products(models.Model):
    Category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=200,null=False,blank=False)
    vendor = models.CharField(max_length=200,null=False,blank=False)
    product_image = models.ImageField(upload_to=getFileName,null=True,blank=True)
    quantity = models.IntegerField(null=False,blank=False)
    original_price = models.FloatField(null=False,blank=False)
    selling_price = models.FloatField(null=False,blank=False)
    description = models.TextField(max_length=500,null=False,blank=False)
    status = models.BooleanField(default=False,help_text="0-show,1-Hidden")
    trending = models.BooleanField(default=False,help_text="0-default,1-Trending")
    created_at = models.DateField(auto_now_add=True)
    delete_product = models.BooleanField(default=False)


    def __str__(self):
        return self.name



class Customer_banner(models.Model):
    name = models.CharField(max_length=50)
    banner_image = models.ImageField(upload_to='banners/')
    status = models.BooleanField()

    def save(self, *args, **kwargs):
        if self.status == 'active':
            self.status = True
        elif self.status == 'inactive':
            self.status = False
        super(Customer_banner, self).save(*args, **kwargs)


class cartItems(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ForeignKey(Products, on_delete=models.CASCADE)
    product_qty = models.IntegerField(null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.CharField(max_length=200)
    
    @property
    def total_cost(self):
        return self.product_qty*self.products.selling_price
    
class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150,null=False,blank=False)
    last_name = models.CharField(max_length=150,null=False,blank=False)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(null = False)
    city = models.CharField(max_length=150,null=False,blank=False)
    state = models.CharField(max_length=150,null=False,blank=False)
    country = models.CharField(max_length=150,null=False,blank=False)
    pincode = models.CharField(max_length=20)
    defaults = models.BooleanField(default=False)
    delete_address = models.BooleanField(default=False)

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=150,null=False,blank=False)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(null=False)
    min_amount = models.IntegerField(default=500)

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    address = models.ForeignKey(Address,on_delete=models.CASCADE)
    coupon = models.ForeignKey(default=1,on_delete=models.CASCADE,to='Accounts.coupon')
    total_price = models.FloatField(null=False)
    payment_mode = models.CharField(max_length=150,null=False)
    discount_price = models.DecimalField(decimal_places=2, default=0, max_digits=10)
    payment_id = models.CharField( max_length=250,null=True)
    order_status = (
        ('Pending','Pending'),
        ('Out for delivery','Out for delivery'),
        ('Completed','Completed'),
        ('Cancel','Cancel'),
        ('Return','Return'),
    )
    status = models.CharField(max_length=150,choices=order_status,default='Pending')
    messages = models.TextField(null=True)
    tracking_no = models.CharField(max_length=150,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} - {}'.format(self.id,self.tracking_no)
    
class Orderitem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    quantity = models.IntegerField(null=False)
    total = models.IntegerField(null=False)

    def __str__(self):
        return '{}' - '{}'.format(self.order.id,self.order.tracking_no)
    
class wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance= models.DecimalField(decimal_places=2, default=0, max_digits=10)
    amount= models.DecimalField(decimal_places=2, default=0, max_digits=10)
    mode = models.CharField(max_length=150, null=True)
    created_at= models.DateField(auto_now_add=True)



