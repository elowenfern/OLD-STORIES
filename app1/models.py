from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,AbstractUser
from django.utils import timezone
from datetime import date
# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model()
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
         
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)
    




class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, blank=True,null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    phone_number=models.CharField(max_length=15,blank=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def _str_(self):
        return self.email
    
class Address(models.Model):
    user      =models.ForeignKey(CustomUser,on_delete=models.CASCADE,null = True,blank=True)
    full_name =models.CharField(max_length=100)
    house_no  =models.CharField(max_length=100)
    post_code =models.CharField(max_length=20)
    state     =models.CharField(max_length=50)
    street    =models.CharField(max_length=100)
    phone_no  =models.CharField(max_length=15,blank=True)
    city      =models.CharField(max_length=100)
    is_default=models.BooleanField(default=False)
class Shipping(models.Model):
    user      =models.ForeignKey(CustomUser,on_delete=models.CASCADE,null = True,blank=True)
    full_name =models.CharField(max_length=100)
    house_no  =models.CharField(max_length=100)
    post_code =models.CharField(max_length=20)
    state     =models.CharField(max_length=50)
    street    =models.CharField(max_length=100)
    phone_no  =models.CharField(max_length=15,blank=True)
    city      =models.CharField(max_length=100)
    is_default=models.BooleanField(default=False)
class Category(models.Model):
    category_name               =   models.CharField(max_length=100)
    description = models.CharField(max_length=1000, default='')
    active                      =   models.BooleanField(default=True)
    category_offer_description = models.CharField(max_length=100, null=True, blank=True)
    category_offer = models.PositiveBigIntegerField(default=0)
    # deleted =models.BooleanField(default=False)
    def __str__(self):
        return self.category_name


class Sub_category(models.Model):
    main_category=models.ForeignKey(Category,on_delete=models.CASCADE)
    sub_category_name=models.CharField(max_length=100)
    active           =   models.BooleanField(default=True)
    def __str__(self):
        return self.sub_category_name
    
class Section(models.Model) :
    name=models.CharField(max_length=100)
    active           =   models.BooleanField(default=True)
    def _str_(self):
        return self.name
    
class Product(models.Model):
   
    product_name   =     models.CharField(max_length=100)
    description    =     models.CharField(max_length=1000,default='')
    category       =     models.ForeignKey(Category, on_delete=models.CASCADE,null=True,blank=True)
    Sub_category   =     models.ForeignKey(Sub_category,on_delete=models.CASCADE,null=True,blank=True)
    min_price      =     models.PositiveIntegerField(default=0)  
    max_price      =     models.PositiveIntegerField(default=0) 
    deleted        =     models.BooleanField(default=False)
    image          =     models.ImageField(upload_to='products/',blank=True,null=True)
    section        =     models.ForeignKey(Section,on_delete=models.CASCADE,blank=True,null=True)
    referral_offer = models.PositiveBigIntegerField(default=0, null=True)
class Images(models.Model):
    product     =  models.ForeignKey(Product, on_delete=models.CASCADE,related_name='product_images')
    images      =  models.ImageField(upload_to='products')


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=200)
    stock= models.IntegerField(default=0)
    deleted        =     models.BooleanField(default=False)
    price =models.IntegerField(blank=True , null=True)
    def apply_discounts(self):
        category_discount = 0
        referral_discount = 0

        # Check if the variation's product has a category offer
        if self.product.category:
            category_discount = self.product.category.category_offer

        # Check if the product has a referral offer
        referral_discount = self.product.referral_offer

        # Calculate the total discount as the sum of category and referral discounts
        total_discount = category_discount + referral_discount
        if referral_discount > 0:
            total_discount += 15
        original_price = self.price  # Store the original price
        discounted_price = original_price - ((total_discount / 100) * original_price)

        return discounted_price


    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.apply_discounts()
        super(Variation, self).save(*args, **kwargs)

class Variation_img(models.Model):
    variation=  models.ForeignKey(Variation,on_delete=models.CASCADE,null=True,blank=True) 
    image = models.ImageField(upload_to='products')
    
class Cart(models.Model):
    user           =     models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True,blank=True)
    variation        =     models.ForeignKey(Variation,on_delete=models.CASCADE,null=True,blank=True)
    quantity       =     models.IntegerField(default=0)
    image          =     models.ImageField(upload_to='products',null=True, blank=True )
    
    @property
    def sub_total(self):
        return self.variation.price * self.quantity

    def _str_(self):
          return f"Cart: {self.user.username} - {self.variation} - Quantity: {self.quantity}"
class Wishlist(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    variation=models.ForeignKey(Variation,on_delete=models.CASCADE,null=True,blank=True)
    image=models.ImageField(upload_to='products',null=True,blank=True)

class Order(models.Model):
        ORDER_STATUS = (
            ('pending', 'Pending'),
            ('processing','processing'),
            ('shipped','shipped'),
            ('delivered','delivered'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('refunded','refunded'),
            ('on_hold','on_hold')
        )
        user           =   models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
        address        =   models.ForeignKey(Address, on_delete=models.CASCADE,null=True, blank=True)
        shipping       =   models.ForeignKey(Shipping, on_delete=models.CASCADE,null=True, blank=True)
        variation      =   models.ForeignKey(Variation, on_delete=models.CASCADE, null=True, blank=True)
        amount         =   models.CharField(max_length=100)  
        payment_type   =   models.CharField(max_length=100)  
        status         =   models.CharField(max_length=100, choices=ORDER_STATUS, default='pending' )  
        date           =   models.DateField(default=date.today)
        def str(self):
            return f"Order #{self.pk} - {self.variation}"

class OrderItem(models.Model):
        order          =   models.ForeignKey(Order,on_delete=models.CASCADE)
        variation        =   models.ForeignKey(Variation,on_delete=models.CASCADE,null=True, blank=True)
        quantity       =   models.IntegerField(default=1)
        image          =   models.ImageField(upload_to='products', null=True, blank=True)
        def str(self):
            return str(self.id)
class Coupon(models.Model):
    coupon_code     =  models.CharField(max_length=100)
    expired         =  models.BooleanField(default=False)
    discount_price  =  models.PositiveIntegerField(default=100)
    minimum_amount  =  models.PositiveIntegerField(default=500)
    expiry_date     =  models.DateField(null=True,blank=True)
    deleted         =  models.BooleanField(default=False)

    def _str_(self):
        return self.coupon_code



    
        

    
    
