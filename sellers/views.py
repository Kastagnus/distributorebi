# views.py
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from sellers.models import CompanyProfile
from users.models import CustomUser
from products.models import Category

class SellerListView(ListView):
    model = CustomUser
    template_name = 'sellers/distributors.html'
    context_object_name = 'sellers'
    paginate_by = 10

    def get_queryset(self):
        category_ids = self.request.GET.getlist('categories')  # Get selected category IDs
        search_term = self.request.GET.get('search', '')
        queryset = CustomUser.objects.filter(is_seller=True)

        if category_ids:
            # Fetch all relevant category IDs including parents and children for selected categories
            selected_category_ids = set(map(int, category_ids))
            relevant_category_ids = set(selected_category_ids)

            for category_id in selected_category_ids:
                category = Category.objects.get(id=category_id)
                # Add parent and child categories if applicable
                if category.level == 2:
                    relevant_category_ids.add(category.parent.id)
                    relevant_category_ids.add(category.parent.parent.id)
                elif category.level == 1:
                    relevant_category_ids.add(category.parent.id)

            # Filter sellers by the relevant categories
            queryset = queryset.filter(
                Q(seller_categories__category_id__in=relevant_category_ids) |
                Q(products__category_id__in=relevant_category_ids)
            ).distinct().order_by('-id')

        if search_term:
            queryset = queryset.filter(
                products__name__icontains=search_term
            ).distinct().order_by('-id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch top-level categories and prefetch related subcategories
        categories = Category.objects.filter(level=0).prefetch_related('subcategories__subcategories')
        context['categories'] = categories
        context['selected_categories'] = self.request.GET.getlist('categories')
        return context

# # Create your views here.

def company_info_view(request, company_id):
    user = get_object_or_404(CustomUser, id=company_id)
    # is_owner = request.user.is_authenticated and request.user == user
    print(user.id)
    company_info = CompanyProfile.objects.get(user=user)
    print("bla", company_info)
    context = {
        'company_info': company_info,
        'user':user
    }

    return render(request, 'sellers/company_info.html', context)
