from django.conf import settings

from cms.models import Title

from minitrue.base import replacer
from minitrue.contrib.django_cms.utils import plugin_get_url

def title_get_url(obj):
    return obj.page.get_absolute_url()

replacer.register(Title, fields=['title', 'page_title', 'menu_title', 'redirect', 'meta_description', 'meta_keywords'],
    urlgetter=title_get_url, select_related=['page'])

if 'cms.plugins.text' in settings.INSTALLED_APPS:
    from cms.plugins.text.models import Text
    replacer.register(Text, fields=['body'], urlgetter=plugin_get_url,
        select_related=['placeholder__page'])

if 'cms.plugins.snippet' in settings.INSTALLED_APPS:
    from cms.plugins.snippet.models import Snippet
    replacer.register(Snippet, fields=['html'], select_related=['placeholder__page'])

if 'cms.plugins.file' in settings.INSTALLED_APPS:
    from cms.plugins.file.models import File
    replacer.register(File, fields=['title'],
        urlgetter=plugin_get_url,
        select_related=['placeholder__page'],
    )

if 'cms.plugins.link' in settings.INSTALLED_APPS:
    from cms.plugins.link.models import Link
    replacer.register(Link, fields=['name'], urlgetter=plugin_get_url,
        select_related=['placeholder__page']
    )

if 'cms.plugins.picture' in settings.INSTALLED_APPS:
    from cms.plugins.picture.models import Picture
    replacer.register(Picture, fields=['alt', 'longdesc'],
        urlgetter=plugin_get_url,
        select_related=['placeholder__page']
    )

if 'cms.plugins.teaser' in settings.INSTALLED_APPS:
    from cms.plugins.teaser.models import Teaser
    replacer.register(Teaser, fields=['title', 'description'],
        urlgetter=plugin_get_url,
        select_related=['placeholder__page']
    )

if 'cms.plugins.twitter' in settings.INSTALLED_APPS:
    from cms.plugins.twitter.models import TwitterRecentEntries, TwitterSearch
    replacer.register(TwitterRecentEntries, fields=['title',],
        urlgetter=plugin_get_url,
        select_related=['placeholder__page']
    )
    replacer.register(TwitterSearch, fields=['title',],
        urlgetter=plugin_get_url,
        select_related=['placeholder__page']
    )