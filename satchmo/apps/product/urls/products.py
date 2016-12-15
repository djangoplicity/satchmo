from django.conf.urls import url
import product
from satchmo_utils.signals import collect_urls

from product.views import get_product, get_price, get_price_detail
from product.views.filters import display_recent, display_bestsellers

urlpatterns = [
    url(r'^(?P<product_slug>[-\w]+)/$',
        get_product, {}, 'satchmo_product'),
    url(r'^(?P<product_slug>[-\w]+)/prices/$',
        get_price, {}, 'satchmo_product_prices'),
    url(r'^(?P<product_slug>[-\w]+)/price_detail/$',
        get_price_detail, {}, 'satchmo_product_price_detail'),
]

urlpatterns += [
    url(r'^view/recent/$',
        display_recent, {}, 'satchmo_product_recently_added'),
    url(r'^view/bestsellers/$',
        display_bestsellers, {}, 'satchmo_product_best_selling'),
]

# here we are sending a signal to add patterns to the base of the shop.
collect_urls.send(sender=product, patterns=urlpatterns, section="product")
