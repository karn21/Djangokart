from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify


CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'SportsWear'),
    ('OW', 'OutWear'),
    ('SN', 'Snack'),
    ('T', 'Technology'),

)


LABEL_CHOICES = (
    ('d', 'danger'),
    ('p', 'primary'),
    ('s', 'secondary')
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(
        choices=CATEGORY_CHOICES, max_length=2, default='S')
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, default='p')
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:product_detail', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('core:add_to_cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('core:remove_from_cart', kwargs={'slug': self.slug})


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.item.title} - {self.quantity}'

    def get_item_price(self):
        if self.item.discount_price:
            return self.item.discount_price
        else:
            return self.item.price

    def get_total_price(self):
        return self.quantity * self.item.price

    def get_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_final_price(self):
        return self.quantity * self.get_item_price()

    def get_savings(self):
        return self.get_total_price() - self.get_discount_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    order_id = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'ShippingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    dispatched = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.pk}'

    def get_order_total(self):
        sum = 0
        for order_item in self.items.all():
            sum += order_item.get_final_price()
        return sum

    def get_coupon_discount(self):
        discount = (self.coupon.discount*self.get_order_total())/100
        return discount

    def get_final_total(self):
        if self.coupon:
            return self.get_order_total() - self.get_coupon_discount()
        else:
            return self.get_order_total()


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    apartment_address = models.CharField(max_length=100)
    country = CountryField()
    zip = models.CharField(max_length=100)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - Address"

    class Meta:
        verbose_name_plural = 'Shipping Addresses'


class Payment(models.Model):
    payment_id = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    discount = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Refund(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    amount = models.FloatField()
    message = models.TextField()
    email = models.EmailField()

    def __str__(self):
        return self.user


@receiver(post_save, sender=Item)
def create_slug(sender, instance, created, **kwargs):
    if created:
        slug_var = instance.title + " " + str(instance.pk)
        instance.slug = slugify(slug_var)
        instance.save()
