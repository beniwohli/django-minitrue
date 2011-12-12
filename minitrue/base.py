from django.db.models.query_utils import Q
from django_load.core import load
from minitrue.utils import MatchIterator, requires_load, build_info

try:
    from johnny import cache
except ImportError:
    cache = None


def get_absolute_url(obj):
    if callable(getattr(obj, 'get_absolute_url', None)):
        try:
            return obj.get_absolute_url()
        except Exception:
            pass
    return None


class ModelReplacer(object):
    def __init__(self, model, **attrs):
        defaults = {
            'fields': [],
            'select_related': [],
            'urlgetter': get_absolute_url,
        }
        self.model = model
        defaults.update(attrs)
        for key, value in defaults.items():
            setattr(self, key, value)
    
    def validate(self):
        for field in self.fields:
            self.model._meta.get_field_by_name(field)
    
    def search_queryset(self, term, case_sensitive):
        q = Q()
        prefix = 'i'
        if case_sensitive:
            prefix = ''
        for field in self.fields:
            q |= Q(**{'%s__%scontains' % (field, prefix): term})
        return self.model.objects.filter(q).select_related(*self.select_related)

    def _search(self, qs, term, replacement, case_sensitive):
        return MatchIterator(qs, term, replacement, case_sensitive, self.urlgetter)
        
    def search(self, term, replacement, case_sensitive):
        return self._search(self.search_queryset(term, case_sensitive), term,
                            replacement, case_sensitive)
    
    def replace(self, queryset, term, replacement, case_sensitive):
        for match in self._search(queryset, term, replacement, case_sensitive):
            match.replace()


class Replacer(object):
    def __init__(self):
        self.models = {}
        self._discovered = False
        
    def discover(self):
        if self._discovered:
            return
        load('searchreplace')
        self._discovered = True
        
    def register(self, model, options=None, **attrs):
        klass = options or ModelReplacer
        instance = klass(model, **attrs)
        instance.validate()
        self.models[model] = instance
    
    def get_options(self, model):
        return self.models[model]

    @requires_load
    def search(self, term, replacement='', case_sensitive=False):
        if cache:
            backend = cache.get_backend()
            backend.unpatch()
        for model, options in self.models.items():
            info = build_info(model, options, term, replacement, case_sensitive)
            yield info, list(options.search(term, replacement, case_sensitive))
        if cache:
            backend.patch()
            
    @requires_load
    def search_querysets(self, term, case_sensitive, *models):
        if not models:
            models = self.models.keys()
        for model in models:
            if model in self.models:
                yield self.models[model].search_queryset(term, case_sensitive)

    @requires_load
    def replace(self, queryset, term, replacement, case_sensitive):
        if cache:
            backend = cache.get_backend()
            backend.unpatch()

        self.models[queryset.model].replace(queryset, term, replacement,
                                            case_sensitive)
        if cache:
            backend.patch()
            cache.invalidate(queryset.model)
    
replacer = Replacer()