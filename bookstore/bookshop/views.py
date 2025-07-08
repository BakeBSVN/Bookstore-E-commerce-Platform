import csv
from django.core.files.temp import NamedTemporaryFile
import requests
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Review
from cart.forms import CartAddProductForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify
from django.views import View
from .forms import CSVUploadForm
from django.core.files import File


# Create your views here.

def index(request):
    top_five_products = Product.objects.all()[:8]
    # showing only 6 categoires in menu bar 
    categories = Category.objects.all()[:6]
    products = Product.objects.all()
    return render(request, 'bookshop/index.html',
                  {'categories': categories, 'products': products, 'top_five_products': top_five_products})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'bookshop/products_list.html', {'category': category,
                                                           'categories': categories,
                                                           'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    reviewproduct = Product.objects.filter(slug=slug)
    prid = None
    for product_id in reviewproduct:
        prid = product_id.id

    all_reviews = Review.objects.filter(product=prid)

    return render(request, 'bookshop/product_detail.html',
                  {'product': product, 'cart_product_form': cart_product_form, 'all_reviews': all_reviews})


def all_Categories(request):
    categories = Category.objects.all()
    return render(request, 'bookshop/all_category_list.html', {'categories': categories})


def contact_us(request):
    return render(request, 'bookshop/contact_us.html')


def search_Result(request):
    if request.method == 'POST':
        searh_query = request.POST['search']
        query_result = Product.objects.filter(name__startswith=searh_query)
        return render(request, 'bookshop/search.html', {'query_result': query_result, 'searh_query': searh_query})


#review 
def Comment_Review(request, product_id):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        rating = request.POST['rating']
        review_comment = request.POST['review']
        product = get_object_or_404(Product, id=product_id)
        comment_review = Review.objects.create(product=product, name=name, email=email, rating=rating,
                                               review_comment=review_comment)
        message = messages.success(request, "Your reviews is submitted")
        return render(request, 'bookshop/product_detail.html')
    return render(request, 'bookshop/product_detail.html')


#upload csv
class CSVUploadView(View):
    def get(self, request):
        form = CSVUploadForm()
        return render(request, 'admin/csv_upload.html', {'form': form})

    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            products = []

            reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
            for row in reader:
                category_name = row['category']
                category_slug = slugify(category_name)
                category, created = Category.objects.get_or_create(name=category_name, slug=category_slug)

                def save_image_from_url(url, filename):
                    response = requests.get(url)
                    if response.status_code == 200:
                        image_file = NamedTemporaryFile(delete=True)
                        image_file.write(response.content)
                        image_file.flush()
                        return image_file
                    return None

                product_name = row['name']
                product_slug = slugify(row['slug']) if row['slug'] else slugify(product_name)
                if Product.objects.filter(slug=product_slug, category=category).exists():
                    continue
                price = row['price']
                try:
                    price = float(price) if price else 0.0
                except ValueError:
                    price = 0.0
                product = Product(
                    name=product_name,
                    slug=product_slug,
                    description=row['description'],
                    price=price,
                    available=row['available'].lower() == 'true',
                    category=category
                )
                if row.get('image_url'):
                    image_path = save_image_from_url(row['image_url'], f"{product_slug}_1.jpg")
                    if image_path:
                        product.image.save(f"{product_slug}_1.jpg", File(image_path))

                if row.get('image_url2'):
                    image_path = save_image_from_url(row['image_url2'], f"{product_slug}_2.jpg")
                    if image_path:
                        product.image2.save(f"{product_slug}_2.jpg", File(image_path))

                if row.get('image_url3'):
                    image_path = save_image_from_url(row['image_url3'], f"{product_slug}_3.jpg")
                    if image_path:
                        product.image3.save(f'{product_slug}_3.jpg', File(image_path))
                products.append(product)

            try:
                Product.objects.bulk_create(products)
                messages.success(request, 'Products have been successfully uploaded.')

            except IntegrityError as e:
                messages.error(request, f"Error uploading products: {e}")

            return redirect('admin:csv_upload')

        return render(request, 'admin/csv_upload.html', {'form': form})
