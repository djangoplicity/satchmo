def active_product_types():
    """Get a list of activated product modules, in the form of
    [(module, config module name),...]
    """
    from django.apps import apps
    gateways = []
    for app in apps.get_app_configs():
        if hasattr(app.models_module, 'SATCHMO_PRODUCT'):
            parts = app.name.split('.')
            module = ".".join(parts)
            if hasattr(app.models_module, 'get_product_types'):
                subtypes = app.models_module.get_product_types()
                for subtype in subtypes:
                    gateways.append((module, subtype))
            else:
                gateways.append((module, parts[-1].capitalize() + 'Product'))

    return gateways
