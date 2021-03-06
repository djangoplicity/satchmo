from decimal import Decimal
from django import http
from django.contrib.messages import constants, get_messages
from django.shortcuts import get_object_or_404, render
from django.template.loader import select_template
from django.utils.translation import ugettext as _
from l10n.utils import moneyfmt
from livesettings.functions import config_value
from product.models import Category, Product
from product.modules.configurable.models import ConfigurableProduct, sorted_tuple
from product.signals import index_prerender
from product.utils import find_best_auto_discount
from satchmo_utils.json import json_encode
from satchmo_utils.numbers import  RoundedDecimalError, round_decimal
from satchmo_utils.views import bad_or_missing
import logging

log = logging.getLogger('product.views')

# ---- Helpers ----

def find_product_template(product, producttypes=None):
    """Searches for the correct override template given a product."""
    if producttypes is None:
        producttypes = product.get_subtypes()

    templates = ["product/detail_%s.html" % x.lower() for x in producttypes]
    templates.append('product/product.html')
    log.debug("finding product template: %s", templates)
    return select_template(templates)

def optionids_from_post(configurableproduct, POST):
    """Reads through the POST dictionary and tries to match keys to possible `OptionGroup` ids
    from the passed `ConfigurableProduct`"""
    chosen_options = []
    for opt_grp in configurableproduct.option_group.all():
        if POST.has_key(str(opt_grp.id)):
            chosen_options.append('%s-%s' % (opt_grp.id, POST[str(opt_grp.id)]))
    return sorted_tuple(chosen_options)

# ---- Views ----
def category_index(request, template="product/category_index.html", root_only=True):
    """Display all categories.

    Parameters:
    - root_only: If true, then only show root categories.
    """
    cats = Category.objects.root_categories()
    ctx = {
        'categorylist' : cats,
    }
    return render(request, template, ctx)

def category_view(request, slug, parent_slugs='', template='product/category.html'):
    """Display the category, its child categories, and its products.

    Parameters:
     - slug: slug of category
     - parent_slugs: ignored
    """
    try:
        category =  Category.objects.get_by_site(slug=slug)
        products = list(category.active_products())
        sale = find_best_auto_discount(products)

    except Category.DoesNotExist:
        return bad_or_missing(request, _('The category you have requested does not exist.'))

    child_categories = category.get_all_children()

    ctx = {
        'category': category,
        'child_categories': child_categories,
        'sale' : sale,
        'products' : products,
    }
    index_prerender.send(Product, request=request, context=ctx, category=category, object_list=products)
    return render(request, template, ctx)


def display_featured(num_to_display=None, random_display=None):
    """
    Used by the index generic view to choose how the featured products are displayed.
    Items can be displayed randomly or all in order
    """
    if num_to_display is None:
        num_to_display = config_value('PRODUCT','NUM_DISPLAY')
    if random_display is None:
        random_display = config_value('PRODUCT','RANDOM_FEATURED')

    q = Product.objects.featured_by_site()
    if not random_display:
        return q[:num_to_display]
    else:
        return q.order_by('?')[:num_to_display]

def get_configurable_product_options(request, id):
    """Used by admin views"""
    cp = get_object_or_404(ConfigurableProduct, product__id=id)
    options = ''
    for og in cp.option_group.all():
        for opt in og.option_set.all():
            options += '<option value="%s">%s</option>' % (opt.id, str(opt))
    if not options:
        return '<option>No valid options found in "%s"</option>' % cp.product.slug
    return http.HttpResponse(options, content_type="text/html")


def get_product(request, product_slug=None, selected_options=(),
    default_view_tax=None):
    """Basic product view"""

    errors = [m for m in get_messages(request) if m.level == constants.ERROR]

    try:
        product = Product.objects.get_by_site(slug=product_slug)
    except Product.DoesNotExist:
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    if not product.active:
        return bad_or_missing(request, _('The product you have requested is currently out of stock.'))

    if default_view_tax is None:
        default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    subtype_names = product.get_subtypes()

    # Save product id for xheaders, in case we display a ConfigurableProduct
    product_id = product.id

    # Clone product object in order to have current product variations in context (extra_context)
    current_product = product

    if 'ProductVariation' in subtype_names:
        selected_options = product.productvariation.unique_option_ids
        #Display the ConfigurableProduct that this ProductVariation belongs to.
        product = product.productvariation.parent.product
        subtype_names = product.get_subtypes()

    best_discount = find_best_auto_discount(product)

    if errors:
        error_message = errors[0]
    else:
        error_message = None

    extra_context = {
        'product': product,
        'current_product' : current_product,
        'default_view_tax': default_view_tax,
        'sale': best_discount,
        'error_message' : error_message,
    }

    # Get the template context from the Product.
    extra_context = product.add_template_context(context=extra_context,
        request=request, selected_options=selected_options,
        default_view_tax=default_view_tax)

    template = find_product_template(product, producttypes=subtype_names)

    response = http.HttpResponse(template.render(extra_context, request))
    try:
        from django.core.xheaders import populate_xheaders
        populate_xheaders(request, response, Product, product_id)
    except ImportError:
        pass
    return response

def get_price(request, product_slug):
    """Get base price for a product, returning the answer encoded as JSON."""
    quantity = Decimal('1')

    try:
        product = Product.objects.get_by_site(active=True, slug=product_slug)
    except Product.DoesNotExist:
        return http.HttpResponseNotFound(json_encode(('', _("not available"))), content_type="text/javascript")

    prod_slug = product.slug

    if request.method == "POST" and request.POST.has_key('quantity'):
        try:
            quantity = round_decimal(request.POST['quantity'], places=2, roundfactor=.25)
        except RoundedDecimalError:
            quantity = Decimal('1.0')
            log.warn("Could not parse a decimal from '%s', returning '1.0'", request.POST['quantity'])

    if 'ConfigurableProduct' in product.get_subtypes():
        cp = product.configurableproduct
        chosen_options = optionids_from_post(cp, request.POST)
        pvp = cp.get_product_from_options(chosen_options)

        if not pvp:
            return http.HttpResponse(json_encode(('', _("not available"))), content_type="text/javascript")
        prod_slug = pvp.slug
        price = moneyfmt(pvp.get_qty_price(quantity))
    else:
        price = moneyfmt(product.get_qty_price(quantity))

    if not price:
        return http.HttpResponse(json_encode(('', _("not available"))), content_type="text/javascript")

    return http.HttpResponse(json_encode((prod_slug, price)), content_type="text/javascript")


def get_price_detail(request, product_slug):
    """Get all price details for a product, returning the response encoded as JSON."""
    results = {
        "success" : False,
        "message" :  _("not available")
    }
    price = None

    if request.method=="POST":
        reqdata = request.POST
    else:
        reqdata = request.GET

    try:
        product = Product.objects.get_by_site(active=True, slug=product_slug)
        found = True

        prod_slug = product.slug

        if reqdata.has_key('quantity'):
            try:
                quantity = round_decimal(reqdata['quantity'], places=2, roundfactor=.25)
            except RoundedDecimalError:
                quantity = Decimal('1.0')
                log.warn("Could not parse a decimal from '%s', returning '1.0'", reqdata['quantity'])
        else:
            quantity = Decimal('1.0')

        if 'ConfigurableProduct' in product.get_subtypes():
            cp = product.configurableproduct
            chosen_options = optionids_from_post(cp, reqdata)
            product = cp.get_product_from_options(chosen_options)

        if product:
            price = product.get_qty_price(quantity)

            results['slug'] = product.slug
            results['price'] = float(price)
            results['success'] = True
            results['message'] = ""

    except Product.DoesNotExist:
        found = False

    data = json_encode(results)
    if found:
        return http.HttpResponse(data, content_type="text/javascript")
    else:
        return http.HttpResponseNotFound(data, content_type="text/javascript")
