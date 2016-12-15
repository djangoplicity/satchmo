from django.conf.urls import url
from django.apps import apps
from livesettings.functions import config_value
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

from payment.views.balance import balance_remaining, balance_remaining_order, \
	charge_remaining, charge_remaining_post
from payment.views.checkout import success
from payment.views.contact import authentication_required, contact_info_view
from payment.views.cron import cron_rebill

import logging

log = logging.getLogger('payment.urls')

ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = [
     url(r'^$', contact_info_view, {'SSL': ssl}, 'satchmo_checkout-step1'),
     url(r'^success/$', success, {'SSL' : ssl}, 'satchmo_checkout-success'),
     url(r'custom/charge/(?P<orderitem_id>\d+)/$', charge_remaining, {}, 'satchmo_charge_remaining'),
     url(r'custom/charge/$', charge_remaining_post, {}, 'satchmo_charge_remaining_post'),
     url(r'^balance/(?P<order_id>\d+)/$', balance_remaining_order, {'SSL' : ssl}, 'satchmo_balance_remaining_order'),
     url(r'^balance/$', balance_remaining, {'SSL' : ssl}, 'satchmo_balance_remaining'),
     url(r'^cron/$', cron_rebill, {}, 'satchmo_cron_rebill'),
     url(r'^mustlogin/$', authentication_required, {'SSL' : ssl}, 'satchmo_checkout_auth_required'),
]

# now add all enabled module payment settings

def make_urlpatterns():
    patterns = []
    for app in apps.get_app_configs():
        if hasattr(app.models_module, 'PAYMENT_PROCESSOR'):
            parts = app.name.split('.')
            key = parts[-1].upper()
            modulename = 'PAYMENT_%s' % key
            name = app.name
            #log.debug('payment module=%s, key=%s', modulename, key)
            # BJK: commenting out Bursar settings here
            # try:
            #     cfg = config_get(modulename, 'INTERFACE_MODULE')
            #     interface = cfg.editor_value
            # except SettingNotSet:
            #     interface = name[:name.rfind('.')]
            # urlmodule = "%s.urls" % interface
            urlmodule = '.'.join(parts) + '.urls'
            urlbase = config_value(modulename, 'URL_BASE')
            log.debug('Found payment processor: %s, adding urls at %s', key, urlbase)
            patterns.append(url(urlbase, [urlmodule, '', '']))
    return tuple(patterns)

urlpatterns += make_urlpatterns()
