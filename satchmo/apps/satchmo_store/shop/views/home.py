from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render
from django.utils.translation import ugettext as _
from livesettings.functions import config_value
from product.views import display_featured
from satchmo_utils.views import bad_or_missing

def home(request, template="shop/index.html"):
    # Display the category, its child categories, and its products.

    if request.method == "GET":
        currpage = request.GET.get('page', 1)
    else:
        currpage = 1

    featured = display_featured()

    count = config_value('PRODUCT','NUM_PAGINATED')

    paginator = Paginator(featured, count)

    is_paged = False
    page = None

    try:
        paginator.validate_number(currpage)
    except InvalidPage:
        return bad_or_missing(request, _("Invalid page number"))

    is_paged = paginator.num_pages > 1
    page = paginator.page(currpage)

    ctx = {
        'all_products_list' : page.object_list,
        'is_paginated' : is_paged,
        'page_obj' : page,
        'paginator' : paginator
    }

    return render(request, template, ctx)

