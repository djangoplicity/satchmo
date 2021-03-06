from satchmo_utils import load_once

load_once('tiered', 'shipping.modules.tieredweight')

def get_methods():
    from shipping.modules.tieredweight.models import Carrier, Shipper
    return [Shipper(carrier) for carrier in Carrier.objects.filter(active=True)]
