from django.http import HttpResponseRedirect
from django.utils import translation
from django.conf import settings
from django.middleware.locale import LocaleMiddleware
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

class DefaultLanguageMiddleware(LocaleMiddleware):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get session language, default to LANGUAGE_CODE
        session_lang = request.session.get('django_language', settings.LANGUAGE_CODE)

        # Set session language if not already set
        if 'django_language' not in request.session:
            request.session['django_language'] = settings.LANGUAGE_CODE
            translation.activate(settings.LANGUAGE_CODE)
            print("I am here")

        # Get current path's language prefix
        path = request.path
        current_prefix = path.split('/')[1] if len(path.split('/')) > 1 else ''
        valid_langs = [lang[0] for lang in settings.LANGUAGES]

        # Redirect if path prefix doesn't match session language
        if current_prefix in valid_langs and current_prefix != session_lang:
            new_path = f'/{session_lang}{path[len(current_prefix) + 1:]}' if current_prefix else f'/{session_lang}{path}'
            return HttpResponseRedirect(new_path)

        # Activate session language
        translation.activate(session_lang)

        return self.get_response(request)