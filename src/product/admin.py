from django.contrib import admin
from .models import ProductVariantPrice, ProductVariant, Product, Variant

admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductVariantPrice)
admin.site.register(Variant)