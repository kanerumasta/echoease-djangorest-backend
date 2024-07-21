from django.core.exceptions import ValidationError
from django.utils.timezone import now

def date_not_future(date_value):
    if date_value > now().date():
        raise ValidationError('Date cannot be a future')


