from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from itertools import zip_longest
from .models import Uzytkownik
import datetime


class AutorField(forms.Field):
    def to_python(self, value):
        fields = ['name', 'surname', 'nick']
        return dict(zip_longest(fields, value.split())) if value else {}

    def validate(self, value):
        super().validate(value)
        if not value.get('name'):
            raise ValidationError('Pole autora nie może być puste.')

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
    album_title = forms.CharField(max_length=50, label='Tytuł albumu')
    album_year = forms.IntegerField(
        label='Rok wydania albumu',
        min_value=1900,
        max_value=datetime.date.today().year,
    )
    file = forms.FileField(widget=forms.ClearableFileInput)


class LyricsUploadForm(forms.Form):
    lyrics = forms.CharField(
        max_length=10_000,
        label='Tekst piosenki (maks. 10 000 znaków)',
        widget=forms.Textarea,
    )


class AddSongToPlaylistForm(forms.Form):
    playlist_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    song_id = forms.IntegerField(label='ID utworu')

    def clean(self):
        from .models import Playlista, Utwor
        cleaned = super().clean()
        playlist_id = cleaned.get('playlist_id')
        song_id = cleaned.get('song_id')
        if playlist_id and not Playlista.objects.filter(pk=playlist_id).exists():
            raise forms.ValidationError('Wybrana playlista nie istnieje.')
        if song_id and not Utwor.objects.filter(pk=song_id).exists():
            raise forms.ValidationError('Wybrany utwór nie istnieje.')
        return cleaned


class PlaylistForm(forms.Form):
    name = forms.CharField(max_length=100, label='Nazwa playlisty')

    def validate_unique_for_user(self, user):
        from .models import Playlista
        name = self.cleaned_data.get('name')
        if Playlista.objects.filter(uzytkownik=user, nazwa=name).exists():
            raise Exception('Masz już playlistę o tej nazwie.')


class HistoryFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False, label='Od',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    date_to = forms.DateField(
        required=False, label='Do',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
