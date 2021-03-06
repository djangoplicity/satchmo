from django.contrib.sites.models import Site
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext_lazy as _
from models import Brand, BrandCategory, BrandProduct
from product import signals
from product.models import Product
from product.utils import find_best_auto_discount

import logging

log = logging.getLogger("satchmo_brand.views")

def brand_list(request):
    brands = Brand.objects.active()
    ctx = {
        'brands' : brands,
    }
    signals.index_prerender.send(Brand, request=request, context=ctx, object_list=brands)
    return render(request, 'brand/index.html', ctx)

def brand_page(request, brandname):
    try:
        brand = Brand.objects.by_slug(brandname)

    except Brand.DoesNotExist:
        raise Http404(_('Brand "%s" does not exist') % brandname)


    products = list(brand.active_products())
    sale = find_best_auto_discount(products)

    ctx = {
        'brand' : brand,
        'products': products,
        'sale' : sale,
    }

    signals.index_prerender.send(BrandProduct, request=request, context=ctx, brand=brand, object_list=products)

    return render(request, 'brand/view_brand.html', ctx)


def brand_category_page(request, brandname, catname):
    try:
        cat = BrandCategory.objects.by_slug(brandname, catname)

    except Brand.DoesNotExist:
        raise Http404(_('Brand "%s" does not exist') % brandname)

    except BrandCategory.DoesNotExist:
        raise Http404(_('No category "%{category}s" in brand "%{brand}s"').format(category=catname, brand=brandname))

    products = list(cat.active_products())
    sale = find_best_auto_discount(products)

    ctx = {
        'brand' : cat,
        'sale' : sale,
    }
    return render(request, 'brand/view_brand.html', ctx)
