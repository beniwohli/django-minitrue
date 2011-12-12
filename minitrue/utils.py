import re

class NULL: pass

RE_CACHE = {}

def plugin_get_url(obj):
    if getattr(obj, "page", None):
        title = obj.page.get_title_obj()
        if title:
            return title.path
    return None

def requires_load(meth):
    def _deco(self, *args, **kwargs):
        self.discover()
        return meth(self, *args, **kwargs)
    _deco.__name__ = meth.__name__
    return _deco

def get_re(term, case_sensitive):
    memokey = '%s%s' % (term, case_sensitive)
    if memokey not in RE_CACHE:
        flags = (re.I,)
        if case_sensitive:
            flags = ()
        RE_CACHE[memokey] = re.compile(re.escape(term), *flags)
    return RE_CACHE[memokey]


def build_info(model, options, term, replacement, case_sensitive):
    info = {}
    info.update(model._meta.__dict__)
    info.update({
        'term': term,
        'replacement': replacement,
        'case_sensitive': case_sensitive,
    })
    return info


class Match(object):
    def __init__(self, instance, app, model, field, pk, data, term, replacement,
                 case_sensitive, url):
        self.instance = instance
        self.app = app
        self.model = model
        self.field = field
        self.pk = pk
        self.data = data
        self.term = term
        self.replacement = replacement
        self.term_re = get_re(term, case_sensitive)
        self.case_sensitive = case_sensitive
        self.url = url
        
    def matchiter(self):
        """
        An iterator that yields tuples of 'content' and whether it should be
        highlighted or not.
        """
        last_end = 0
        for match in self.term_re.finditer(self.data):
            start, end = match.start(), match.end()
            if start != last_end:
                yield self.data[last_end:start], False
            yield self.data[start:end], True
            last_end = end
        trailing = self.data[last_end:]
        if trailing:
            yield trailing, False
            
    def replace(self):
        new = self.term_re.sub(self.replacement, self.data)
        setattr(self.instance, self.field, new)
        self.instance.save()


def match_factory(obj, term, replacement, case_sensitive, url):
    from minitrue.base import replacer
    opts = replacer.get_options(obj.__class__)
    for field in opts.fields:
        data = getattr(obj, field, NULL)
        if data and data is not NULL and get_re(term, case_sensitive).search(data):
            yield Match(
                obj,
                obj._meta.app_label,
                obj._meta.object_name.lower(),
                field,
                obj.pk,
                data,
                term,
                replacement,
                case_sensitive,
                url,
            )


class MatchIterator(object):
    def __init__(self, queryset, term, replacement, case_sensitive, urlgetter):
        self.queryset = queryset
        self._cached_results = None
        self._cached_length = None
        self.term = term
        self.replacement = replacement
        self.case_sensitive = case_sensitive
        self.urlgetter = urlgetter
    
    def __iter__(self):
        if self._cached_results is None:
            self._cached_results = []
            self._cached_length = 0
            for obj in self.queryset:
                url = self.urlgetter(obj)
                matches = match_factory(obj, self.term, self.replacement,
                                        self.case_sensitive, url)
                for match in matches:
                    self._cached_results.append(match)
                    self._cached_length += 1
                    yield match
        else:
            for match in self._cached_results:
                yield match
    
    def __nonzero__(self):
        return bool(len(self))
    
    def __len__(self):
        if self._cached_length is None:
            list(iter(self))
        return self._cached_length