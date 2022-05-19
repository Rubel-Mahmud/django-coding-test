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


class UpdateProductView(generic.TemplateView):
    template_name = 'products/update.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateProductView, self).get_context_data(**kwargs)
        product = {}
        images = []
        product_variant = []
        product_variant_prices = []

        prd = Product.objects.get(pk=kwargs['id'])

        product['id'] = kwargs['id']
        product['title'] = prd.title
        product['sku'] = prd.sku
        product['description'] = prd.description
        product['images'] = images

        prd_variants = ProductVariant.objects.filter(product=prd)
        sizes = prd_variants.filter(variant=1).values_list('variant_title', flat=True).distinct()
        colors = prd_variants.filter(variant=2).values_list('variant_title', flat=True).distinct()
        styles = prd_variants.filter(variant=3).values_list('variant_title', flat=True).distinct()
        if sizes:
            print(sizes)
            product_variant.append({
                'option':1, 'tags':list(sizes.all())
            })
        if colors:
            print(colors)
            product_variant.append({
                'option':2, 'tags':list(colors.all())
            })
        if styles:
            print(styles)
            product_variant.append({
                'option':3, 'tags':list(styles.all())
            })
        
        prd_vr_prices = ProductVariantPrice.objects.filter(product=prd)
        for item in prd_vr_prices:
            titles = ''
            titles += item.product_variant_one.variant_title + '/'
            if item.product_variant_two != None:
                titles += item.product_variant_two.variant_title + '/'

            if item.product_variant_three != None:
                titles += item.product_variant_three.variant_title + '/'
            
            product_variant_prices.append({
                'title':titles, 'price':item.price, 'stock':item.stock, 'id': item.id
            })


        product['product_variant'] = product_variant
        product['product_variant_prices'] = product_variant_prices
        
        variants = Variant.objects.filter(active=True).values('id', 'title')

        context['product'] = product
        context['variants'] = list(variants.all())

        return context





@method_decorator(csrf_exempt, name='dispatch')
class UpdateProductDoneView(View):

    def post(self, request):
        json_data = request.body
        # convert json data into python native data type
        productInfos = json.loads(json_data) 

        # Product Model Info
        id = productInfos['product_id']
        title = productInfos['title']
        sku = productInfos['sku']
        description = productInfos['description']
        product = Product.objects.get(pk=id)
        product.title = title
        product.sku = sku
        product.description = description
        product.save()

        product_variant_prices = productInfos['product_variant_prices']
        for prd_var_price in product_variant_prices:
            # title = prd_var_price['title']
            price = prd_var_price['price']
            stock = prd_var_price['stock'] 

            # prd_variants = title.split('/')
            # if prd_variants.__contains__(''):
            #     prd_variants.remove('')

            items = ProductVariantPrice.objects.filter(product=product)
            print("items : ",items)
            if prd_var_price.__contains__('id'):
                item = items.get(id=prd_var_price['id'])
                item.price = price
                item.stock = stock
                item.save()
            else:
                print("ProductVariantPrice id doesn't exist\n")

        return HttpResponse('Product has updated successfully')





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
            if prd_variants.__contains__(''):
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




class ProductListView(View):

    def is_valid_querypram(self, pram):
        return pram != '' and pram is not None

    def get(self, request):
        context = {}
        context['variants'] = Variant.objects.all()
        products = Product.objects.all().order_by('-created_at')

        title = request.GET.get('title')
        variant = request.GET.get('variant')
        price_from = request.GET.get('price_from')
        price_to = request.GET.get('price_to')
        date = request.GET.get('date')

        if self.is_valid_querypram(title):
            products = Product.objects.filter(title__contains=title)
            context['title'] = title
        if self.is_valid_querypram(variant):
            products = Product.objects.filter(productvariantprice__product_variant_one__variant_title__icontains=variant)
            if not products:
                products = Product.objects.filter(productvariantprice__product_variant_two__variant_title__icontains=variant)
            if not products:
                products = Product.objects.filter(productvariantprice__product_variant_three__variant_title__icontains=variant)
        if self.is_valid_querypram(price_from):
            products = Product.objects.filter(productvariantprice__price__gte=price_from).distinct()
            context['price_from'] = price_from
        if self.is_valid_querypram(price_to):
            products = Product.objects.filter(productvariantprice__price__lte=price_to).distinct()
        if self.is_valid_querypram(price_from) and self.is_valid_querypram(price_to):
            products = Product.objects.filter(productvariantprice__price__gte=price_from, productvariantprice__price__lte=price_to).distinct()    
        if self.is_valid_querypram(date):
            print("Date : ", date)
            products = Product.objects.filter(created_at__date=date)
            print("Products : ", products.count())

        paginator = Paginator(products, 5)
        page_number = request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        
        return render(request, 'products/list.html', context)