from cms.models.titlemodels import Title
from minitrue.base import replacer

replacer.register(Title, fields=['title', 'redirect'])