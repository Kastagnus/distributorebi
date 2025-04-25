from libretranslatepy import LibreTranslateAPI
from langdetect import detect, DetectorFactory
from django.core.cache import cache
from django.utils.translation import get_language

DetectorFactory.seed = 0

def translate_product(product):
    cache_key = f"product_{product.id}_{get_language()}"
    cached = cache.get(cache_key)
    if cached:
        return cached['name'], cached['description']

    translator = LibreTranslateAPI("https://libretranslate.de/")  # Public instance
    target_language = get_language()

    try:
        name_lang = detect(product.name) if product.name.strip() else 'ka'
        desc_lang = detect(product.description) if product.description.strip() else 'ka'
    except:
        name_lang = desc_lang = 'ka'

    translated_name = product.name
    translated_description = product.description

    try:
        if name_lang != target_language:
            translated_name = translator.translate(product.name, name_lang, target_language)
        if desc_lang != target_language and product.description.strip():
            translated_description = translator.translate(product.description, desc_lang, target_language)
    except Exception as e:
        print(f"Translation error: {e}")

    cache.set(cache_key, {'name': translated_name, 'description': translated_description}, timeout=3600)
    return translated_name, translated_description