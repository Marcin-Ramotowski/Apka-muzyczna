from django.db import models
from django.contrib.auth.models import User


class Autor(models.Model):
    class Meta:
        db_table = "autor"
    autor_id = models.IntegerField(primary_key=True)
    imie = models.CharField(max_length=30)
    nazwisko = models.CharField(max_length=50)
    pseudonim = models.CharField(max_length=40)
    wiecej_info = models.TextField()

    def __str__(self):
        pseudonim = f'"{self.pseudonim}"' if self.pseudonim else ''
        return f'{self.imie} {self.nazwisko} {pseudonim}'


class Album(models.Model):
    class Meta:
        db_table = "album"
    album_id = models.IntegerField(primary_key=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='albums')
    tytul = models.CharField(max_length=50)
    rok_wydania = models.SmallIntegerField()
    wiecej_info = models.TextField()

    def __str__(self):
        autor = Autor.objects.filter(autor_id=self.autor_id).first()
        return f'{self.tytul} {autor}'


class Utwor(models.Model):
    class Meta:
        db_table = "utwor"
    utwor_id = models.IntegerField(primary_key=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='songs_by_autor')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs_in_album')
    tytul = models.CharField(max_length=60)
    gatunek = models.CharField(max_length=30)
    dlugosc = models.TimeField()

    def __str__(self):
        autor = Autor.objects.filter(autor_id=self.autor_id).first()
        duration = str(self.dlugosc)[3:]
        return f'{self.tytul} {autor} {duration}'


class Uzytkownik(models.Model):
    class Meta:
        db_table = "uzytkownik"
    ACCOUNTS_TYPES = (
        ('FR', 'free'),
        ('PR', 'premium')
    )

    uzytkownik_id = models.IntegerField(primary_key=True)
    nazwa_uzytkownika = models.CharField(max_length=50)
    haslo = models.CharField(max_length=82)
    typ_konta = models.CharField(choices=ACCOUNTS_TYPES, max_length=7, default='free')

    def __str__(self):
        return self.nazwa_uzytkownika


class Playlista(models.Model):
    class Meta:
        db_table = "playlista"
    playlista_id = models.IntegerField(primary_key=True)
    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='playlists')
    nazwa = models.CharField(max_length=100)

    def __str__(self):
        user = Uzytkownik.objects.filter(uzytkownik_id=self.uzytkownik_id).first()
        return f'{self.nazwa} {user}'


class PlaylistaUtwor(models.Model):
    class Meta:
        db_table = "playlista_utwor"
    playlista = models.ForeignKey(Playlista, on_delete=models.CASCADE, related_name='playlistSongs_playlists')
    utwor = models.ForeignKey(Utwor, on_delete=models.CASCADE, related_name='playlistSongs_songs')


class Subskrypcja(models.Model):
    class Meta:
        db_table = "subskrypcja"
    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='subscriptions_user')
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='subscriptions_author')
