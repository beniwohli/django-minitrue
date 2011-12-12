from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect, HttpResponseBadRequest, 
    HttpResponseNotAllowed, HttpResponse, HttpResponseForbidden)
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from minitrue.forms import SearchAndReplaceForm, ReplaceForm, ReplaceSingleForm
from minitrue.models import SearchAndReplace


class NewSearchAdmin(admin.ModelAdmin):
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        info = "%s_%s" % (self.model._meta.app_label, self.model._meta.module_name)
        pat = lambda regex, fn: url(regex, self.admin_site.admin_view(fn), name='%s_%s' % (info, fn.__name__))

        url_patterns = patterns('',
            pat(r'replace/$', self.replace),
            pat(r'replace-all/$', self.replace_all),
        )

        return url_patterns + super(NewSearchAdmin, self).get_urls()
    
    def add_view(self, request):
        return HttpResponseRedirect(reverse('admin:minitrue_searchandreplace_changelist'))
    
    def has_change_permission(self, *args, **kwargs):
        return False
    has_delete_permission = has_change_permission
    
    def changelist_view(self, request, extra_context=None):
        if not self.has_add_permission(request):
            return HttpResponseForbidden()
        results = []
        term = ''
        replacement = ''
        form = SearchAndReplaceForm(request.GET)
        if form.is_valid():
            term = form.cleaned_data['term']
            replacement = form.cleaned_data['replacement']
            results = form.get_results()
        else:
            form = SearchAndReplaceForm()
        data = RequestContext(request)
        data['form'] = form
        data['results'] = results
        data['term'] = term
        data['replacement'] = replacement
        data['title'] = _("Search and Replace")
        return render_to_response('minitrue/search_and_replace.html', data)
    
    def replace(self, request):
        if not self.has_add_permission(request):
            return HttpResponseForbidden()
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        form = ReplaceSingleForm(request.POST)
        if form.is_valid():
            form.replace()
            return HttpResponse()
        return HttpResponseBadRequest(form.errors.as_text())
    
    def replace_all(self, request):
        if not self.has_add_permission(request):
            return HttpResponseForbidden()
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        form = ReplaceForm(request.POST)
        if form.is_valid():
            form.replace()
            return HttpResponse()
        return HttpResponseBadRequest(form.errors.as_text())


admin.site.register(SearchAndReplace, NewSearchAdmin)
