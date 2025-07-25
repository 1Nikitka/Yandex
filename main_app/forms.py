from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Форма регистрации пользователя
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Форма поиска
class SearchForm(forms.Form):
    city = forms.CharField(label='Города', required=True, help_text='Введите города через запятую')
    keywords = forms.CharField(label='Ключевые слова', required=True, help_text='Введите ключевые слова через запятую')
    pages_count = forms.IntegerField(label='Количество страниц', min_value=1, max_value=10, initial=1)
