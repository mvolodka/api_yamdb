import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(year):
    """Year field validation."""
    current_year = dt.date.today().year
    if year > current_year or year < 1:
        raise ValidationError(
            'Значение года не может быть больше текущего или меньше 1.'
        )
