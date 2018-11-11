import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class ASCIIDotlessUsernameValidator(validators.RegexValidator):
    regex = r'^[\w@+-]+$'
    message = _(
        'Introduce un nombre de usuario valido. Este valor solo debe contener letras, '
        'numeros, y @/+/-/_.'
    )
    flags = re.ASCII

validators = [ASCIIDotlessUsernameValidator()]