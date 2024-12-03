from django.urls import path, reverse_lazy
from django.views.i18n import set_language

from .views import home, RegistrationView, MyLoginView, test_view
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetCompleteView, \
    PasswordResetDoneView, PasswordResetConfirmView

urlpatterns = [
    path('home/', home, name='home'),
    path("", home, name='home'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),
    path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset-done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name="password_reset_done"),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
        name="password_reset_confirm"  # Correct placement
    ),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name="password_reset_complete"),
    path('set-language/', set_language, name='set_language'),

]
