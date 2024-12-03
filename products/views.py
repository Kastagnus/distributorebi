from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from products.models import Category
from users.models import CustomUser
from django.db.models.query import Q


from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
# from .forms import ProductForm

from django.shortcuts import render, get_object_or_404
from .models import Product
from users.models import CustomUser
from sellers.models import CompanyProfile

def company_dashboard(request, company_id):
    # Fetch the company and its products
    user = get_object_or_404(CustomUser, id=company_id)
    categories = Category.objects.filter(level=0).prefetch_related('subcategories__subcategories')
    products = Product.objects.filter(seller=user)

    # Check if the user is the owner of the company
    is_owner = request.user.is_authenticated and request.user == user

    context = {
        'user': user,
        'products': products,
        'is_owner': is_owner,  # Used in the template to show additional actions
        'categories': categories
    }

    return render(request, 'products/products.html', context)

# def add_product(request):
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.owner = request.user  # Assuming 'owner' links product to user
#             product.save()
#             return redirect('company_dashboard')
#     return redirect('company_dashboard')
# def delete_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id, owner=request.user)
#     product.delete()
#     return redirect('company_dashboard')
