# views.py
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView

from products.forms import CompanyProfileForm
from sellers.models import CompanyProfile, BranchContact
from users.models import CustomUser
from products.models import Category
from regions.models import City, Region


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

@login_required
def edit_company_profile(request, company_id):
    user = get_object_or_404(CustomUser, id=company_id)
    company_info = get_object_or_404(CompanyProfile, user=user)

    if request.user != user:
        return redirect('some_error_page')

    if request.method == 'POST':
        # Update user fields
        user.brand_name = request.POST.get('brand_name')
        user.ltd_name = request.POST.get('ltd_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.save()

        # Update company profile fields
        company_info.about_us = request.POST.get('about_us')
        company_info.address = request.POST.get('address')
        company_info.website = request.POST.get('website')
        company_info.facebook = request.POST.get('facebook')
        company_info.twitter = request.POST.get('twitter')
        company_info.linkedin = request.POST.get('linkedin')

        # Update cities from POST
        city_ids = request.POST.getlist('cities')  # Get list of checked city IDs
        company_info.cities.set(city_ids)

        # Handle branch contacts
        company_info.branch_contacts.all().delete()
        branch_counter = 1
        while f'branch_name_{branch_counter}' in request.POST:
            name = request.POST.get(f'branch_name_{branch_counter}')
            position = request.POST.get(f'branch_position_{branch_counter}')
            phone = request.POST.get(f'branch_phone_{branch_counter}')
            region = request.POST.get(f'branch_region_{branch_counter}')
            if name and position and phone and region:
                BranchContact.objects.create(
                    company=company_info,
                    contact_name=name,
                    position=position,
                    phone_number=phone,
                    region=region
                )
            branch_counter += 1

        company_info.save()
        return redirect('dashboard', company_id=company_id)

    # Fetch all regions with their cities for the template
    regions = Region.objects.prefetch_related('cities').all()
    print("Regions:", list(regions))
    print("Company Cities:", list(company_info.cities.all()))
    print("Displayyyy")
    return render(request, 'sellers/company_info.html', {
        'user': user,
        'company_info': company_info,
        'regions': regions,
    })