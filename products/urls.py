from django.urls import path
from .views import dashboard, load_subcategories, \
    ProductUpdateView, ProductDeleteView

urlpatterns = [
    # Company Dashboard
    path('dashboard/<int:company_id>/', dashboard, name='dashboard'),
    path('load-subcategories/', load_subcategories, name='load_subcategories'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

]