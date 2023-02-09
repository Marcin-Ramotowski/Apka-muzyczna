from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Uzytkownik


class AutorField(forms.Field):
    def to_python(self, value):
        return value.split() if value else []

    def validate(self, value):
        super().validate(value)
        name, surname, nick = value
        if not name.isalpha() or not surname.isalpha():
            raise ValidationError('Podaj prawidłowe imię i nazwisko')

    def clean(self, value):
        result = super().clean(value)
        return result


class AlbumField(forms.Field):
    def to_python(self, value):
        return value.split(', ') if value else []

    def validate(self, value):
        super().validate(value)
        year: str = value[1]
        if not year.isdigit():
            raise ValidationError('Rok wydania podany po przecinku musi być liczbą',
                                  params={'album': 'niepoprawny rok'})

    def clean(self, value):
        result = super().clean(value)
        return result


class LoginForm(forms.Form):
    login = forms.CharField(label='Login', max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())


class SearchForm(forms.Form):
    DATABASE_CHOICES = (('autor', 'autor'), ('piosenka', 'piosenka'), ('album', 'album'),
                        ('playlista', 'playlista'))
    database = forms.CharField(label='Co chcesz znaleźć?', widget=forms.RadioSelect(choices=DATABASE_CHOICES))
    query = forms.CharField(label='Szukaj:', max_length=30)


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Imię:", max_length=20)
    last_name = forms.CharField(label="Nazwisko:", max_length=20)
    email = forms.EmailField()

    class Meta:
        model = Uzytkownik
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')


class UploadForm(forms.Form):
    title = forms.CharField(max_length=30, label='Tytuł')
    genre = forms.CharField(max_length=20, label='Gatunek')
    autor = AutorField(label='Autor', widget=forms.TextInput(attrs={'placeholder': 'Imię nazwisko pseudonim'}))
    album = AlbumField(label='Album', widget=forms.TextInput(attrs={'placeholder': 'Tytuł, rok wydania'}))
    file = forms.FileField(widget=forms.ClearableFileInput)
