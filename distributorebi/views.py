# views.py
from django.conf import settings
from django.shortcuts import redirect

def redirect_to_default_language(request):
    return redirect(f'/{settings.LANGUAGE_CODE}/')
