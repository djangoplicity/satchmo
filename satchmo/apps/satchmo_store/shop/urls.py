from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from django.contrib.sitemaps.views import sitemap

from product.urls import urlpatterns as productpatterns
from satchmo_store import shop
from satchmo_store.shop.views.sitemaps import sitemaps
from satchmo_store.shop.views.cart import add, add_ajax, add_multiple, \
	agree_terms, display, remove, remove_ajax, set_quantity, set_quantity_ajax
from satchmo_store.shop.views.contact import form
from satchmo_store.shop.views.home import home
from satchmo_store.shop.views.orders import order_history, order_tracking
from satchmo_store.shop.views.search import search_view
from satchmo_store.shop.views.smart import smart_add
from satchmo_utils.signals import collect_urls

urlpatterns = shop.get_satchmo_setting('SHOP_URLS')

urlpatterns += [
    url(r'^$', home, {}, 'satchmo_shop_home'),
    url(r'^add/$', smart_add, {}, 'satchmo_smart_add'),
    url(r'^cart/$', display, {}, 'satchmo_cart'),
    url(r'^cart/accept/$', agree_terms, {}, 'satchmo_cart_accept_terms'),
    url(r'^cart/add/$', add, {}, 'satchmo_cart_add'),
    url(r'^cart/add/ajax/$', add_ajax, {}, 'satchmo_cart_add_ajax'),
    url(r'^cart/qty/$', set_quantity, {}, 'satchmo_cart_set_qty'),
    url(r'^cart/qty/ajax/$', set_quantity_ajax, {}, 'satchmo_cart_set_qty_ajax'),
    url(r'^cart/remove/$', remove, {}, 'satchmo_cart_remove'),
    url(r'^cart/remove/ajax/$', remove_ajax, {}, 'satchmo_cart_remove_ajax'),
    url(r'^checkout/', include('payment.urls')),
    url(r'^contact/$', form, {}, 'satchmo_contact'),
    url(r'^history/$', order_history, {}, 'satchmo_order_history'),
    url(r'^quickorder/$', add_multiple, {}, 'satchmo_quick_order'),
    url(r'^tracking/(?P<order_id>\d+)/$', order_tracking, {}, 'satchmo_order_tracking'),
    url(r'^search/$', search_view, {}, 'satchmo_search'),
]

# here we add product patterns directly into the root url
urlpatterns += productpatterns

urlpatterns += [
    url(r'^contact/thankyou/$',
        TemplateView.as_view(template_name='shop/contact_thanks.html'), {},
        'satchmo_contact_thanks'),
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': sitemaps},
        'satchmo_sitemap_xml'),

]

# here we are sending a signal to add patterns to the base of the shop.
collect_urls.send(sender=shop, patterns=urlpatterns)
