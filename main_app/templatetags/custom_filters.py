from django import template

register = template.Library()

@register.filter
def split_by_plus(value):
    """
    Делит строку по символу "+" и возвращает список номеров, добавляя + обратно.
    Игнорирует пустые элементы.
    """
    if not value:
        return []
    if isinstance(value, list):  # уже список
        return value
    if not isinstance(value, str):
        value = str(value)
    # Убираем первый пустой элемент, если строка начинается с "+"
    parts = [part for part in value.split('+') if part]
    return [f"+{part.strip()}" for part in parts]
