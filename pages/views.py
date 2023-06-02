from django.shortcuts import render, get_object_or_404
from .models import ExchangePage, StaticPage
from exchange.models import Currency
from sdk.lang_dict import lang_dict
from sdk.lang_js_dict import lang_js_dict


def exchange_pair(request, slug):
    l = list(Currency.objects.all())
    rates4Andrey = []
    page = get_object_or_404(ExchangePage, slug=slug)
    for i in l:
        for j in l:
            if i != j:
                rates4Andrey.append(i.title + "_" + j.title)
    context = {
        'allrates': rates4Andrey,
        'exchange_page': page,
        'lang_dict': lang_dict,
        'lang_js_dict': lang_js_dict,
        'cur1': page.currency_from,
        'cur2': page.currency_to
    }
    return render(request, 'main.html', context)


def about_us(request):
    page = StaticPage.objects.get(slug='about-us')
    return render(request, 'static.html', {'page': page})
