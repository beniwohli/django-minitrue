from django.contrib.sites.models import Site

SITE_CACHE = {}

def plugin_get_url(obj):

    if getattr(obj, "page", None):
        domain = '/'
        title = obj.page.get_title_obj()
        if title and title.path:
            if obj.page.site_id != Site.objects.get_current().pk:
                domain = 'http://%s/%s/' % (_get_domain_from_cache(obj.page.site_id), title.language)
            return domain + title.path
    return None

def _get_domain_from_cache(site_id):
    if not site_id in SITE_CACHE:
        SITE_CACHE[site_id] = Site.objects.get(pk=site_id).domain
    return SITE_CACHE[site_id]
