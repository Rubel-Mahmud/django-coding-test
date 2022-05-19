from django.urls import path
from django.views.generic import TemplateView

from product.views.product import CreateProductView, SaveProductInfoView, ProductListView, UpdateProductView, UpdateProductDoneView
from product.views.variant import VariantView, VariantCreateView, VariantEditView

app_name = "product"

urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),

    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('update/<int:id>/', UpdateProductView.as_view(), name='update.product'),
    path('update/done/', UpdateProductDoneView.as_view(), name='update_done.product'),
    path('save/', SaveProductInfoView.as_view(), name='save.product'),
    path('list/', ProductListView.as_view(), name='list.product')
    # path('list/', TemplateView.as_view(template_name='products/list.html', extra_context={
    #     'product': True
    # }), name='list.product'),
]
