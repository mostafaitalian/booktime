from decimal import Decimal

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, F, Q, Sum
#from django.db.models.aggregates import Count


# Create your models here.
class ActiveProductManager(models.Manager):
    def active(self):
        return self.filter(active=True)
class AdvancedProductQueries(models.Manager):
    def get_advanced_products(self):
        return self.filter(Q(price__lte=Decimal('2.00'))|Q(producttag__name__startswith='the'))

class Product(models.Model):
    tags = models.ManyToManyField("ProductTag", related_name='products', blank=True)
    name = models.CharField(help_text='enter the product name', max_length=80)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=80)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_uploaded = models.DateTimeField(auto_now=True)
    objects = ActiveProductManager()      
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product-images")
    thumbnail = models.ImageField(null=True, upload_to="product_thumbnails")
    def __str__(self):
        return self.product.name
    
    
class ProductTag(models.Model):
    
    name= models.CharField(max_length=60)
    slug = models.SlugField(max_length=60)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('you shoud specify an email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') == False:
            raise ValueError('superuser must be staff')
        if extra_fields.get('is_superuser') == False:
            raise ValueError('superuser must be superuser')
        return self._create_user(email, password, **extra_fields)
class User(AbstractUser):
    email = models.EmailField('enter ur email', unique=True)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    @property
    def is_employee(self):
        return self.is_active and (self.is_superuser or self.is_staff and self.groups.filter(name="Employees").exist())
    def is_dispatcher(self):
        return self.is_active and (self.is_superuser or self.is_staff and self.groups.filter(name="Dispatchers").exist())   
class Address(models.Model):
    status = (('eg', 'EGYPT'), ('ita', 'ITALY'))
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    address1 = models.CharField('enter ur address', max_length=200)
    address2 = models.CharField('enter additional address', max_length=200)
    country_code = models.CharField(blank=True, max_length=3, default="+")
    phone_number = models.PositiveIntegerField(blank=True, validators=[MaxValueValidator(9999999)])
    zip_code = models.PositiveIntegerField()
    country = models.CharField(choices=status, max_length=8)
    def __str__(self):
        return self.address1 + '-' + self.user.email
class Basket(models.Model):
    OPEN = 10
    SUBMITTED = 20
    CANCELED = 30
    STATUSES = ((OPEN, 'open'), (SUBMITTED, 'submitted'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    def is_empty(self):
        return self.lines.all().count() == 0

    def count(self):
        return sum(i.quantity for i in self.lines.all())
    def create_order(self, billing_address, shipping_address):
        if not self.user:
            raise Basket.ValidationError("basket should have user, please login or signup")
        order_data = {
            'user': self.user,
            'billing_name': billing_address.name,
            'billing_address1': billing_address.address1,
            'billing_address2': billing_address.address2,
            'billing_country_code': billing_address.country_code,
            'billing_phone_number': billing_address.phone_number,
            'billing_zip_code': billing_address.zip_code,
            'billing_country': billing_address.country,
            'shipping_name': shipping_address.name,
            'shipping_address1': shipping_address.address1,
            'shipping_address2': shipping_address.address2,
            'shipping_country_code': shipping_address.country_code,
            'shipping_phone_number': shipping_address.phone_number,
            'shipping_zip_code': shipping_address.zip_code,
            'shipping_country': shipping_address.country,            
        }
        order = Order.objects.create(**order_data)
        for line in self.lines.all():
            for item in range(line.quantity):
                order_line_data = {
                    'order': order,
                    'product': line.product
                }
                order_line = OrderLine.objects.create(**order_line_data)
        self.status = Basket.SUBMITTED
        self.save()
        return order

class BasketLine(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])        
class Order(models.Model):
    NEW = 10
    PAID = 20
    DONE = 30
    CANCELLED = 40
    STATUSES = ((NEW, 'New'), (PAID, 'Paid'), (DONE, 'Done'), (CANCELLED, 'Cancelled'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_spoken_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="cs_chats", null=True)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    billing_name = models.CharField(max_length=60)
    billing_address1 = models.CharField('enter ur address', max_length=200)
    billing_address2 = models.CharField('enter additional address', max_length=200)
    billing_country_code = models.CharField(blank=True, max_length=3, default="+")
    billing_phone_number = models.PositiveIntegerField(blank=True, validators=[MaxValueValidator(9999999)])
    billing_zip_code = models.PositiveIntegerField()
    billing_country = models.CharField(max_length=8)
    shipping_name = models.CharField(max_length=60)
    shipping_address1 = models.CharField('enter ur address', max_length=200)
    shipping_address2 = models.CharField('enter additional address', max_length=200)
    shipping_country_code = models.CharField(blank=True, max_length=3, default="+")
    shipping_phone_number = models.PositiveIntegerField(blank=True, validators=[MaxValueValidator(9999999)])
    shipping_zip_code = models.PositiveIntegerField()
    shipping_country = models.CharField(max_length=8)
    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def mobile_thumb_url(self):
        products = [i.product for i in self.order_lines.all()]
        if products:
            image = products[0].productimage_set.first()
        if image:
            return image.thumbnail.url
    @property
    def total_price(self):
        products = [i.product for i in self.order_lines.all()]
        if products:
            total_price=0
            for product in products:
                total_price += product.price
        return total_price  
    @property
    def total_price_2(self):
        res = self.order_lines.aggregate(total_price=Sum('product__price'))
        return res['total_price']
    @property
    def summary(self):
        product_count = self.order_lines.values("product__name").annotate(c=Count('product__name'))
        pieces = []
        for pc in product_count:
            pieces.append("%s - %s" % (pc["c"], pc['product__name']))
        return ", ".join(pieces)


class OrderLine(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40
    STATUSES = ((NEW, 'New'), (PROCESSING, 'Processing'), (SENT, 'Sent'), (CANCELLED, 'Cancelled'))    
    order = models.ForeignKey(Order, related_name='order_lines', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUSES, default=NEW)
