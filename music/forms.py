from django import forms


class LoginForm(forms.Form):
    login = forms.CharField(label='Login', max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())


class SearchForm(forms.Form):
    DATABASE_CHOICES = (('autor', 'autor'), ('piosenka', 'piosenka'), ('album', 'album'),
                        ('playlista', 'playlista'))
    database = forms.CharField(label='Co chcesz znaleźć?', widget=forms.RadioSelect(choices=DATABASE_CHOICES))
    query = forms.CharField(label='Szukaj:', max_length=30)
