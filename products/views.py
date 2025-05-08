from urllib import request

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET
from django.views.generic import UpdateView, DeleteView
from regions.models import Region
from .forms import ProductCreateForm
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import CustomUser, Product, Category, TranslationCache
from sellers.models import CompanyProfile
from google.cloud import translate_v2 as translate
from django.utils.translation import get_language


def dashboard(request, company_id):
    user = get_object_or_404(CustomUser, id=company_id)
    is_owner = request.user.is_authenticated and request.user == user
    products = Product.objects.filter(seller=user).order_by('-id')
    company_info = CompanyProfile.objects.get(user=user)
    category_ids = list(products.values_list('category', flat=True).distinct())
    regions = Region.objects.prefetch_related('cities').all()
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            # Determine the appropriate category
            level_2_category = form.cleaned_data.get('level_2_category')
            level_1_category = form.cleaned_data.get('level_1_category')
            level_0_category = form.cleaned_data.get('level_0_category')
            if level_2_category:
                product.category = level_2_category
            elif level_1_category:
                product.category = level_1_category
            elif level_0_category:
                product.category = level_0_category
            else:
                form.add_error(None, "Please select a valid category.")
                return render(request, 'products/products.html', {
                    'user': user,
                    'is_owner': is_owner,
                    'company_info': company_info,
                    'regions': regions,
                    'form': form,
                    'categories': Category.objects.filter(level=0).prefetch_related('subcategories__subcategories'),
                    'selected_categories': request.GET.getlist('categories'),
                    'products': products,
                    'page_obj': Paginator(products, 3).get_page(request.GET.get('page')),
                })
            product.save()
            return redirect('dashboard', company_id=user.id)
    else:
        form = ProductCreateForm()

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

    paginator = Paginator(products, 10)
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
        'regions': regions,
        "form": form,
        "language_code": get_language(),
    }

    langg = get_language()
    print(langg)
    print(request.META.get('HTTP_ACCEPT_LANGUAGE'))
    print(request.session.get('django_language'))
    print(f"Middleware: Path={request.path}, Session Language={request.session.get('django_language')}")
    return render(request, 'products/products.html', context)

# View to load subcategories dynamically
# def load_subcategories(request):
#     category_id = request.GET.get('category_id')
#     level = int(request.GET.get('level', 0))
#     subcategories = []
#     if category_id:
#         subcategories = Category.objects.filter(parent_id=category_id).values('id', 'name')
#         return JsonResponse(list(subcategories), safe=False)
#
#     return JsonResponse({'subcategories': []})
@require_GET
def load_subcategories(request):
    category_id = request.GET.get('category_id')
    level = int(request.GET.get('level', 0))
    language_code = request.GET.get('language_code')  # Default to Georgian ('ka')
    print("langggg", language_code)

    # Map language code to field name
    name_field = {
        'ka': 'name',
        'en': 'name_en',
        'ru': 'name_ru'
    }.get(language_code, 'name')  # Fallback to 'name' if language_code is invalid

    subcategories = []
    if category_id:
        # Fetch subcategories with the translated name field
        subcategories = Category.objects.filter(parent_id=category_id).values('id', name_field)
        # Rename the field to 'name' in the response for consistency
        subcategories = [{'id': cat['id'], 'name': cat[name_field] or Category.objects.get(id=cat['id']).name}
                         for cat in subcategories]

    return JsonResponse(subcategories, safe=False)

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductCreateForm
    template_name = 'products/product_form.html'

    def get_object(self, queryset=None):
        """Override get_object to ensure the product belongs to the logged-in user."""
        product = get_object_or_404(Product, id=self.kwargs.get('pk'))
        if product.seller != self.request.user:
            raise PermissionDenied("You are not allowed to edit this product.")
        lng = get_language()
        print(lng, "from uipdateview")
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['language_code'] = get_language()
        return context

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