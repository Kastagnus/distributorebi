from django.urls import path
from .views import dashboard, load_subcategories, \
    ProductUpdateView, ProductDeleteView, ProductCreateView

urlpatterns = [
    # Company Dashboard
    path('dashboard/<int:company_id>/', dashboard, name='dashboard'),
    path('add_product/', ProductCreateView.as_view(), name='add_product'),
    path('load-subcategories/', load_subcategories, name='load_subcategories'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),


    # Company Actions (for authenticated users only)
    # path('company/<int:company_id>/modify/', views.modify_company, name='modify_company'),
    # path('company/<int:company_id>/delete/', views.delete_company, name='delete_company'),
    #
    # # Product Actions
    # path('product/add/', views.add_product, name='add_product'),  # Add product
    # path('product/<int:product_id>/modify/', views.modify_product, name='modify_product'),  # Modify product
    # path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),  # Delete product
]