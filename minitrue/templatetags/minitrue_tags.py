from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import InclusionTag, AsTag
from django import template


register = template.Library()


class RenderMatchBits(InclusionTag):
    template = 'minitrue/inc/match_bits.html'
    options = Options(
        Argument('matchiter')
    )
    
    
    def get_context(self, context, matchiter):
        return {'matchiter': matchiter}

register.tag(RenderMatchBits)


class Counter(object):
    def __init__(self):
        self.value = 0
        
    def incr(self):
        self.value += 1
        return ''
    
    def __unicode__(self):
        return unicode(self.value)


class ResultCounter(AsTag):
    options = Options(
        'as',
        Argument('varname', resolve=False)
    )
    
    def get_value(self, context):
        return Counter()
    
    
register.tag(ResultCounter)