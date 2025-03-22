from django.contrib.auth.forms import UserCreationForm
from django.core.cache import cache
from django.db.models import Prefetch
from django.shortcuts import render
from django.contrib.auth.views import FormView, LoginView
from django.urls import reverse_lazy
from django.core.mail import send_mail

from products.models import Category
from .forms import UserForm, MyLoginForm
from distributorebi import settings
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.utils.translation import activate
from .models import CustomUser


class RegistrationView(FormView):
    template_name = 'users/register.html'
    form_class = UserForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        # user.is_active = False #activate it for user checking
        user.username = form.cleaned_data['email']
        user.is_seller = True
        print(form.cleaned_data)
        user.save()
        self.send_user_info_to_admin(user)
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid")
        print("Errors:", form.errors)

        # Re-render the form with errors
        return self.render_to_response(self.get_context_data(form=form))

    def send_user_info_to_admin(self, user):
        subject = "New user registration"
        message = (f"""
        You have new user
        User Details:
        Email: {user.email}
        Full Name: {user.full_name}
        LTD Name: {user.ltd_name}
        Phone Number: {user.phone_number}
        """)
        email_to = "ucha95@gmail.com"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email_to])


class MyLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')
    form_class = MyLoginForm
    def form_invalid(self, form):
        print(form.cleaned_data)
        print("Form is invalid")
        print("Errors:", form.errors)
        return self.render_to_response(self.get_context_data(form=form))

def home(request):
    recent_companies = CustomUser.objects.filter(is_seller=True).order_by('-date_joined').prefetch_related('companyprofile')[:9]

    cache_key = 'top_level_categories'
    categories = cache.get(cache_key)
    if not categories:
        categories = Category.objects.filter(level=0).prefetch_related('subcategories')[:6]
        cache.set(cache_key, categories, timeout=60 * 60)  # Cache for 1 hour

    context = {
        'sellers': recent_companies,
        'categories': categories,
    }
    return render(request, 'home.html', context)

# Create your views here.

def test_view(request):
    # Force Georgian translation
    activate('ka')
    return HttpResponse(_("Log In"))

