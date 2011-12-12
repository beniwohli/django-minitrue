from django import forms
from django.db.models.loading import get_model
from minitrue.base import replacer
from minitrue.utils import match_factory


class SearchAndReplaceForm(forms.Form):
    term = forms.CharField()
    replacement = forms.CharField(required=False)
    case_sensitive = forms.BooleanField(initial=False, required=False)
    
    def get_results(self):
        return replacer.search(
            self.cleaned_data['term'],
            self.cleaned_data['replacement'],
            self.cleaned_data['case_sensitive'],
        )


def _fake_url_getter(obj):
    return None


class ReplaceSingleForm(forms.Form):
    term = forms.CharField()
    replacement = forms.CharField()
    model = forms.CharField()
    app = forms.CharField()
    pk = forms.CharField()
    field = forms.CharField()
    case_sensitive = forms.BooleanField(initial=False, required=False)
    
    def clean(self):
        data = super(ReplaceSingleForm, self).clean()
        model_class = get_model(data['app'], data['model'])
        instance = model_class.objects.get(pk=data['pk'])
        data['instance'] = instance
        data['model_class'] = model_class
        return data
    
    def replace(self):
        instance = self.cleaned_data['instance']
        term = self.cleaned_data['term']
        replacement = self.cleaned_data['replacement']
        case_sensitive = self.cleaned_data['case_sensitive']
        for match in match_factory(instance, term, replacement, case_sensitive,
                                   _fake_url_getter):
            if match.field == self.cleaned_data['field']:
                match.replace()


class ReplaceForm(forms.Form):
    term = forms.CharField()
    replacement = forms.CharField()
    model = forms.CharField()
    app = forms.CharField()
    case_sensitive = forms.BooleanField(initial=False, required=False)
    
    def clean(self):
        data = super(ReplaceForm, self).clean()
        model_class = get_model(data['app'], data['model'])
        term = self.cleaned_data['term']
        case_sensitive = self.cleaned_data['case_sensitive']
        queryset = list(replacer.search_querysets(term, case_sensitive, model_class))[0]
        data['queryset'] = queryset
        return data
    
    def replace(self):
        replacer.replace(
            self.cleaned_data['queryset'],
            self.cleaned_data['term'],
            self.cleaned_data['replacement'],
            self.cleaned_data['case_sensitive'],
        )