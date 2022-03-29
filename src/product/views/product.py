import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.views import View, generic

from product.models import Variant, Product, ProductVariant, ProductVariantPrice


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


@method_decorator(csrf_exempt, name='dispatch')
class SaveProductInfoView(View):

    def post(self, request):
        json_data = request.body
        # convert json data into python native data type
        productInfos = json.loads(json_data) 

        # Product Model Info
        title = productInfos['title']
        sku = productInfos['sku']
        description = productInfos['description']
        product = Product.objects.create(title=title, sku=sku, description=description)


        # ProductVariant Model Info
        product_variants = productInfos['product_variant']
        for prdVariant in product_variants:
            variant = Variant.objects.get(id=prdVariant['option'])
            tags = prdVariant['tags']
            for tag in tags:
                ProductVariant.objects.create(variant_title=tag, variant=variant, product=product)

        # ProductVariantPrice Model Info
        product_variant_prices = productInfos['product_variant_prices']
        for prd_var_price in product_variant_prices:
            title = prd_var_price['title']
            price = prd_var_price['price']
            stock = prd_var_price['stock'] 
            product_variant_one = None
            product_variant_two = None
            product_variant_three = None

            prd_variants = title.split('/')
            prd_variants.remove('')

            if len(prd_variants) == 3:
                product_variant_one = ProductVariant.objects.filter(variant_title=prd_variants[0]).get(product=product)
                product_variant_two = ProductVariant.objects.filter(variant_title=prd_variants[1]).get(product=product)
                product_variant_three = ProductVariant.objects.filter(variant_title=prd_variants[2]).get(product=product)
            elif len(prd_variants) == 2:
                product_variant_one = ProductVariant.objects.filter(variant_title=prd_variants[0]).get(product=product)
                product_variant_two = ProductVariant.objects.filter(variant_title=prd_variants[1]).get(product=product)
            elif len(prd_variants) == 1:
                product_variant_one = ProductVariant.objects.filter(variant_title=prd_variants[0]).get(product=product)

            ProductVariantPrice.objects.create(product_variant_one=product_variant_one,product_variant_two=product_variant_two, product_variant_three=product_variant_three,price=price, stock=stock, product=product)
            prd_variants = []

        return HttpResponse('Recieved posted data successfuly..')



def is_valid_querypram(pram):
        return pram != '' and pram is not None


class ProductListView(View):

    def get(self, request):
        context = {}
        context['variants'] = Variant.objects.all()
        products = Product.objects.all().order_by('-created_at')

        title = request.GET.get('title')
        variant = request.GET.get('variant')
        price_from = request.GET.get('price_from')
        price_to = request.GET.get('price_to')
        date = request.GET.get('date')

        if is_valid_querypram(title):
            products = Product.objects.filter(title__contains=title)
        if is_valid_querypram(variant):
            products = Product.objects.filter(productvariantprice__product_variant_one__variant_title__icontains=variant)
            if not products:
                products = Product.objects.filter(productvariantprice__product_variant_two__variant_title__icontains=variant)
            if not products:
                products = Product.objects.filter(productvariantprice__product_variant_three__variant_title__icontains=variant)
        if is_valid_querypram(price_from):
            products = Product.objects.filter(productvariantprice__price__gte=price_from)
            context['price_from'] = price_from
        if is_valid_querypram(price_to):
            products = Product.objects.filter(productvariantprice__price__lt=price_to)
        if is_valid_querypram(date):
            products = Product.objects.filter(created_at=date)

        paginator = Paginator(products, 5)
        page_number = request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        
        return render(request, 'products/list.html', context)