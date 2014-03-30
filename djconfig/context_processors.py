import djconfig


def config(request):
    """
    Simple context processor that puts the config into every
    RequestContext. Just make sure you have a setting like this:

        TEMPLATE_CONTEXT_PROCESSORS = (
            # ...
            'djconfig.context_processors.config',
        )
    """
    return {"config": djconfig.config, }