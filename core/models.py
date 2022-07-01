from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, null=False, blank=False, on_delete=models.CASCADE)

    # Extra fields
    phone_field = models.CharField(max_length=12, blank=False)

    def __str__(self) :
        return self.user.username

# Category model
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    def __str__(self):
        return self.category_name

class Product(models.Model):
    poster = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
    description = models.CharField(max_length=200, blank=True)
    price = models.FloatField(default=0.0, blank=True)
    quantity = models.IntegerField(default=0, blank=True)
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=15, blank=True) 
    phone = models.CharField(max_length=12, null=True)
    image = models.ImageField(upload_to='images/', blank=True)
    available = models.BooleanField(default=True, blank=True)


    def get_add_to_cart_url(self):
        return reverse('core:add-to-cart', kwargs={
            'pk' : self.pk
        })

    def __str__(self):
        return self.name

    def get_poster_name(self):
        return self.poster

    def get_poster_phone(self):
        return self.phone

    def get_product_name(self):
        return self.name



class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return f"{self.product.quantity} of {self.product.name}"

    def get_total_item_price(self):
        return self.product.quantity * self.product.price

    def get_final_price(self):
        return self.get_total_item_price()

    def get_product(self):
        return self.product



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    order_id = models.CharField(max_length=100, unique=True, default=None, blank=True, null=True)
    datetime_of_payment = models.DateTimeField(auto_now_add=True)
    order_delivered = models.BooleanField(default=False)
    order_received = models.BooleanField(default=False)
    
    razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)



    def save(self, *args, **kwargs):
        if self.order_id is None and self.datetime_of_payment and self.id:
            self.order_id = self.datetime_of_payment.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        
        return super().save(*args, **kwargs)

    
    def __str__(self):
        return self.user.username

    
    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    
    def get_process_fee(self):
        final_price = self.get_total_price()
        process_fee = 0
        if final_price <= 1000:
            process_fee = 0.15 * final_price
        elif final_price <= 5000:
            process_fee = 0.20 * final_price
        else:
            process_fee = 0.25 * final_price
        return process_fee
        

    def get_grand_total(self):
        grand_total = 0
        grand_total = self.get_total_price() + self.get_process_fee()
        return grand_total

    def get_user(self):
        return self.user



class CheckoutAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username




    









