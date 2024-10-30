from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, View, ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django import forms
from .models import Product
from .utils import ImageLocalStorage


class Home(TemplateView):
    template_name = "pages/home.html"


class About(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "About us - Online Store",
            "subtitle": "About us",
            "description": "This is an about page...",
            "author": "Developed by: Martin Betancur",
        })
        return context


class Contact(TemplateView):
    template_name = "pages/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Contact - Online Store",
            "subtitle": "Contact",
            "mail": "martin@eafit.edu.co",
            "phone": "3010000000",
            "address": "UNIVERSIDAD EAFIT",
            "author": "Developed by: Martin Betancur",
        })
        return context


class ProductIndex(View):
    template_name = 'products/index.html'

    def get(self, request):
        viewData = {}
        viewData["title"] = "Products - Online Store"
        viewData["subtitle"] = "List of products"
        viewData["products"] = Product.objects.all()
        return render(request, self.template_name, viewData)


class ProductShow(View):
    template_name = 'products/show.html'

    def get(self, request, id):
        try:
            product_id = int(id)
            if product_id < 1:
                raise ValueError("Product id must be 1 or greater")
            product = get_object_or_404(Product, pk=product_id)
        except (ValueError, IndexError):
            return HttpResponseRedirect(reverse('home'))

        viewData = {}
        viewData["title"] = product.name + " - Online Store"
        viewData["subtitle"] = product.name + " - Product information"
        viewData["product"] = product
        return render(request, self.template_name, viewData)


class ProductList(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Products - Online Store'
        context['subtitle'] = 'List of products'
        return context


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'price']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0 and price is not None:
            raise forms.ValidationError("Price must be greater than zero.")
        return price


class ProductCreate(View):
    template_name = 'products/create.html'

    def get(self, request):
        form = ProductForm()
        viewData = {}
        viewData["title"] = "Create product"
        viewData["form"] = form
        return render(request, self.template_name, viewData)

    def post(self, request):
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
        else:
            viewData = {}
            viewData["title"] = "Create product"
            viewData["form"] = form
            return render(request, self.template_name, viewData)


class Success(View):
    template_name = 'products/success.html'

    def get(self, request):
        return render(request, self.template_name)


class Cart(View):
    template_name = 'cart/index.html'

    def get(self, request):
        products = {}
        products[121] = {'name': 'Tv samsung', 'price': '1500'}
        products[11] = {'name': 'Iphone', 'price': '4000'}

        cart_products = {}
        cart_product_data = request.session.get('cart_product_data', {})

        for key, product in products.items():
            if str(key) in cart_product_data.keys():
                cart_products[key] = product

        view_data = {
            'title': 'Cart - Online Store',
            'subtitle': 'Shopping Cart',
            'products': products,
            'cart_products': cart_products
        }
        return render(request, self.template_name, view_data)

    def post(self, request, product_id):
        cart_product_data = request.session.get('cart_product_data', {})
        cart_product_data[product_id] = product_id
        request.session['cart_product_data'] = cart_product_data
        return redirect('cart_index')


class CartRemoveAll(View):

    def post(self, request):
        if 'cart_product_data' in request.session:
            del request.session['cart_product_data']

        return redirect('cart_index')

    
def ImageFactory(image_storage):

    class Image(View):
        template_name = 'images/images.html'

        def get(self, request):
            image_url = request.session.get('image_url', '')
            return render(request, self.template_name,
                          {'image_url': image_url})

        def post(self, request):
            image_url = image_storage.store(request)
            request.session['image_url'] = image_url
            return redirect('image_index')

    return Image


class ImageViewNoDI(View):
    template_name = 'imagesnotid/index.html'

    def get(self, request):
        image_url = request.session.get('image_url', '')
        return render(request, self.template_name, {'image_url': image_url})

    def post(self, request):
        image_storage = ImageLocalStorage()
        image_url = image_storage.store(request)
        request.session['image_url'] = image_url
        return redirect('image_index')
