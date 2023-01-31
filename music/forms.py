from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Uzytkownik


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
    file = forms.FileField(widget=forms.ClearableFileInput)
