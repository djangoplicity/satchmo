def active_gateways():
    """Get a list of activated payment gateways, in the form of
    [(module, config module name),...]
    """
    from django.apps import apps
    gateways = []
    for app in apps.get_app_configs():
        if hasattr(app.models_module, 'PAYMENT_PROCESSOR'):
            parts = app.name.split('.')
            module = ".".join(parts)
            group = 'PAYMENT_%s' % parts[-1].upper()
            gateways.append((module, group))
    return gateways
