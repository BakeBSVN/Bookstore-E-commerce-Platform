from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.template.defaultfilters import slugify
import requests


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    image2 = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    image3 = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)

    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[str(self.slug)])

    @staticmethod
    def get_exchange_rate():
        # Sử dụng API để lấy tỷ giá hối đoái từ USD sang VND
        try:
            response = requests.get(
                'https://api.exchangerate-api.com/v4/latest/USD'
            )
            data = response.json()
            return data['rates']['VND']
        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
            return 23000

    def price_in_vnd(self):
        exchange_rate = self.get_exchange_rate()
        return self.price * exchange_rate

    def set_price_in_vnd(self, vnd_price):
        exchange_rate = self.get_exchange_rate()
        self.price = vnd_price / exchange_rate
        self.save()


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=20)
    rating = models.IntegerField(default=1)
    review_comment = models.TextField(max_length=200)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.product.name
