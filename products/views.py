from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import ProductCreateForm
# views.py
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import CustomUser, Product, Category
from sellers.models import CompanyProfile



def dashboard(request, company_id):
    user = get_object_or_404(CustomUser, id=company_id)
    is_owner = request.user.is_authenticated and request.user == user
    products = Product.objects.filter(seller=user).order_by('-id')
    company_info = CompanyProfile.objects.get(user=user)
    category_ids = list(products.values_list('category', flat=True).distinct())
    relevant_category_ids = set(category_ids)

    for category_id in category_ids:
        category = Category.objects.get(id=category_id)

        # Add parents of level 2 categories
        if category.level == 2:
            if category.parent:
                relevant_category_ids.add(category.parent.id)
                if category.parent.parent:
                    relevant_category_ids.add(category.parent.parent.id)

        # Add parents of level 1 categories
        elif category.level == 1:
            if category.parent:
                relevant_category_ids.add(category.parent.id)

    # Fetch all relevant categories
    categories = Category.objects.filter(id__in=relevant_category_ids, level=0).prefetch_related(
        'subcategories__subcategories')

    # Filter subcategories and sub-subcategories within each category
    for category in categories:
        # Filter subcategories that have products listed by this seller
        category.filtered_subcategories = category.subcategories.filter(id__in=relevant_category_ids)

        # For each filtered subcategory, filter the sub-subcategories that have products listed by this seller
        for subcategory in category.filtered_subcategories:
            subcategory.filtered_sub_subcategories = subcategory.subcategories.filter(id__in=relevant_category_ids)

    selected_categories = request.GET.getlist('categories')
    if selected_categories:
        products = products.filter(category__id__in=selected_categories)

    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'user': user,
        'is_owner': is_owner,
        'categories': categories,
        'selected_categories': selected_categories,
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'company_info': company_info,
    }
    return render(request, 'products/products.html', context)


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductCreateForm
    template_name = 'products/product_create_form.html'
    success_url = reverse_lazy('sellers')

    def form_valid(self, form):
        # Determine the appropriate category
        level_2_category = form.cleaned_data.get('level_2_category')
        level_1_category = form.cleaned_data.get('level_1_category')
        level_0_category = form.cleaned_data.get('level_0_category')
        form.instance.seller = self.request.user
        if level_2_category:
            form.instance.category = level_2_category
        elif level_1_category:
            form.instance.category = level_1_category
        elif level_0_category:
            form.instance.category = level_0_category
        else:
            form.add_error(None, "Please select a valid category.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard', kwargs={'company_id': self.request.user.id})

# View to load subcategories dynamically
def load_subcategories(request):
    category_id = request.GET.get('category_id')
    print("hello", category_id)
    level = request.GET.get('level')

    if category_id:
        subcategories = Category.objects.filter(parent_id=category_id)
        return JsonResponse(list(subcategories.values('id', 'name')), safe=False)
    return JsonResponse({'subcategories': []})

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductCreateForm
    template_name = 'products/product_form.html'

    def get_object(self, queryset=None):
        """Override get_object to ensure the product belongs to the logged-in user."""
        product = get_object_or_404(Product, id=self.kwargs.get('pk'))
        if product.seller != self.request.user:
            raise PermissionDenied("You are not allowed to edit this product.")
        return product

    def get_success_url(self):
        return reverse_lazy('dashboard', kwargs={'company_id': self.request.user.id})
class ProductDeleteView(DeleteView):
    model = Product

    def get_object(self, queryset=None):
        """Override get_object to ensure the product belongs to the logged-in user."""
        product = get_object_or_404(Product, id=self.kwargs.get('pk'))
        if product.seller != self.request.user:
            raise PermissionDenied("You are not allowed to delete this product.")
        return product

    def get_success_url(self):
        return reverse_lazy('dashboard', kwargs={'company_id': self.request.user.id})



# def company_dashboard(request, company_id):
#     # Fetch the company and its products
#     user = get_object_or_404(CustomUser, id=company_id)
#     is_owner = request.user.is_authenticated and request.user == user
#     products = Product.objects.filter(seller=user).order_by('-id')
#     categories = Category.objects.filter(level=0).prefetch_related('subcategories__subcategories')
#     # selected_categories = request.GET.getlist('categories')
#     # print(selected_categories)
#
#     # Get all categories that have products listed by this seller
#     category_ids = list(products.values_list('category', flat=True).distinct())
#
#     # Set to keep track of all relevant category IDs
#     relevant_category_ids = set(category_ids)
#
#     # Add selected state to categorize
#     for category_id in category_ids:
#         category = Category.objects.get(id=category_id)
#
#         # Add parents of level 2 categories
#         if category.level == 2:
#             if category.parent:
#                 relevant_category_ids.add(category.parent.id)
#                 if category.parent.parent:
#                     relevant_category_ids.add(category.parent.parent.id)
#
#         # Add parents of level 1 categories
#         elif category.level == 1:
#             if category.parent:
#                 relevant_category_ids.add(category.parent.id)
#
#     # Fetch all relevant categories
#     categories = Category.objects.filter(id__in=relevant_category_ids, level=0).prefetch_related(
#         'subcategories__subcategories')
#
#     # Filter subcategories and sub-subcategories within each category
#     for category in categories:
#         # Filter subcategories that have products listed by this seller
#         category.filtered_subcategories = category.subcategories.filter(id__in=relevant_category_ids)
#
#         # For each filtered subcategory, filter the sub-subcategories that have products listed by this seller
#         for subcategory in category.filtered_subcategories:
#             subcategory.filtered_sub_subcategories = subcategory.subcategories.filter(id__in=relevant_category_ids)
#
#     # Fetch parent and grandparent categories for level 1 and level 2 categories
#
#     # Filtering products by selected categories (if any)
#     selected_categories = request.GET.getlist('categories')
#
#
#     context = {
#         'user': user,
#         'is_owner': is_owner,
#         'categories': categories,
#         'selected_categories': selected_categories,
#
#     }
#     return render(request, 'products/products.html', context)
#
# def product_list(request, company_id):
#     user = get_object_or_404(CustomUser, id=company_id)
#     products = Product.objects.filter(seller=user).order_by('-id')
#     # print(products)
#     selected_categories = request.GET.getlist('categories')
#     print(selected_categories)
#
#     # if selected_categories:
#     #     products = products.filter(category__id__in=selected_categories)
#
#     paginator = Paginator(products, 3)
#     page_number = request.GET.get('page')
#     print(page_number)
#     page_obj = paginator.get_page(page_number)
#     # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#     #     print('I am here')
#     #
#     #     html = render_to_string('products/product_list.html', {'products': page_obj.object_list, 'page_obj': page_obj}, request=request)
#     #     print(html)
#     #     return JsonResponse({'html': html})
#
#     return render(request, 'products/product_list.html', {'products': page_obj.object_list, 'page_obj': page_obj})
#
#
# def filter_form_view(request, company_id):
#     # Get the categories and selected filters
#     user = get_object_or_404(CustomUser, id=company_id)
#     products = Product.objects.filter(seller=user).order_by('-id')
#     categories = Category.objects.filter(level=0).prefetch_related('subcategories__subcategories')
#     selected_categories = request.GET.getlist('categories')
#
#     # Get all categories that have products listed by this seller
#     category_ids = list(products.values_list('category', flat=True).distinct())
#
#     # Set to keep track of all relevant category IDs
#     relevant_category_ids = set(category_ids)
#
#     # Add selected state to categorize
#     for category_id in category_ids:
#         category = Category.objects.get(id=category_id)
#
#         # Add parents of level 2 categories
#         if category.level == 2:
#             if category.parent:
#                 relevant_category_ids.add(category.parent.id)
#                 if category.parent.parent:
#                     relevant_category_ids.add(category.parent.parent.id)
#
#         # Add parents of level 1 categories
#         elif category.level == 1:
#             if category.parent:
#                 relevant_category_ids.add(category.parent.id)
#
#     # Fetch all relevant categories
#     categories = Category.objects.filter(id__in=relevant_category_ids, level=0).prefetch_related(
#         'subcategories__subcategories')
#
#     # Filter subcategories and sub-subcategories within each category
#     for category in categories:
#         # Filter subcategories that have products listed by this seller
#         category.filtered_subcategories = category.subcategories.filter(id__in=relevant_category_ids)
#
#         # For each filtered subcategory, filter the sub-subcategories that have products listed by this seller
#         for subcategory in category.filtered_subcategories:
#             subcategory.filtered_sub_subcategories = subcategory.subcategories.filter(id__in=relevant_category_ids)
#
#     return render(request, 'products/filter_form.html', {
#         'categories': categories,
#         'selected_categories': selected_categories,
#     })
