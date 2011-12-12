from filer.models import Image as FilerImage
from filer.models import File as FilerFile
from minitrue.base import replacer

replacer.register(FilerImage, fields=['default_alt_text', 'default_caption', 'description'])
replacer.register(FilerFile, fields=['description'],)
