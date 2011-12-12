from simplegallery.models import (Gallery, Image as GalleryImage, CarouselImage,
                                  CarouselFeature)

from minitrue.base import replacer

from minitrue.contrib.django_cms.utils import plugin_get_url

replacer.register(Gallery, fields=['name', 'title', 'description'], urlgetter=plugin_get_url,
    select_related=['placeholder__page'])
replacer.register(GalleryImage, fields=['title', 'description'])
replacer.register(CarouselImage, fields=['title', 'description', 'url'])
replacer.register(CarouselFeature, fields=['title'], urlgetter=plugin_get_url,
    select_related=['placeholder__page'])