from django import http
from django.contrib.sites.models import Site
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from forms import GiftCertCodeForm, GiftCertPayShipForm
from models import GiftCertificate, GIFTCODE_KEY
from livesettings.functions import config_get_group
from satchmo_store.shop.models import Order
from payment.utils import pay_ship_save, get_or_create_order
from payment.views import confirm, payship
from satchmo_utils.dynamic import lookup_url
from django.contrib.sites.models import Site
import logging
from django.core.urlresolvers import reverse


log = logging.getLogger("giftcertificate.views")

gc = config_get_group('PAYMENT_GIFTCERTIFICATE')


def giftcert_pay_ship_process_form(request, contact, working_cart, payment_module, allow_skip):
    if request.method == "POST":
        new_data = request.POST.copy()
        form = GiftCertPayShipForm(request, payment_module, new_data)
        if form.is_valid():
            data = form.cleaned_data

            # Create a new order.
            newOrder = get_or_create_order(request, working_cart, contact, data)
            newOrder.add_variable(GIFTCODE_KEY, data['giftcode'])

            request.session['orderID'] = newOrder.id

            url = None
            gift_certificate = GiftCertificate.objects.get(code=data['giftcode'], valid=True,
                    site=Site.objects.get_current())
            # Check to see if the giftcertificate is not enough
            # If it isn't, then process it and prompt for next payment method
            if gift_certificate.balance < newOrder.balance:
                controller = confirm.ConfirmController(request, gc)
                controller.confirm()
                url = reverse('satchmo_balance_remaining')
            else:
                url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
    else:
        form = GiftCertPayShipForm(request, payment_module)

    return (False, form)


def pay_ship_info(request):
    return payship.base_pay_ship_info(request,
        gc,
        giftcert_pay_ship_process_form,
        template="shop/checkout/giftcertificate/pay_ship.html")

def confirm_info(request, template="shop/checkout/giftcertificate/confirm.html"):
    try:
        order = Order.objects.get(id=request.session['orderID'])
        giftcert = GiftCertificate.objects.from_order(order)
    except (Order.DoesNotExist, GiftCertificate.DoesNotExist, KeyError):
        giftcert = None

    controller = confirm.ConfirmController(request, gc)
    controller.templates['CONFIRM'] = template
    controller.extra_context={'giftcert' : giftcert}
    controller.confirm()
    return controller.response

def check_balance(request):
    if request.method == "GET":
        code = request.GET.get('code', '')
        if code:
            try:
                gc = GiftCertificate.objects.get(code=code,
                    value=True,
                    site=Site.objects.get_current())
                success = True
                balance = gc.balance
            except GiftCertificate.DoesNotExist:
                success = False
        else:
            success = False

        ctx = {
            'code' : code,
            'success' : success,
            'balance' : balance,
            'giftcertificate' : gc
        }
    else:
        form = GiftCertCodeForm()
        ctx = {
            'code' : '',
            'form' : form
        }
    return render(request, 'giftcertificate/balance.html', ctx)
