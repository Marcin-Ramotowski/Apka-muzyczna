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


class Album(models.Model):
    class Meta:
        db_table = "album"
    album_id = models.IntegerField(primary_key=True)
    autor_id = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='albums')
    tytul = models.CharField(max_length=50)
    rok_wydania = models.SmallIntegerField()
    wiecej_info = models.TextField()


class Utwor(models.Model):
    class Meta:
        db_table = "utwor"
    utwor_id = models.IntegerField(primary_key=True)
    autor_id = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='songs_by_autor')
    album_id = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs_in_album')
    tytul = models.CharField(max_length=60)
    gatunek = models.CharField(max_length=30)
    dlugosc = models.DurationField()


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


class Playlista(models.Model):
    class Meta:
        db_table = "playlista"
    playlista_id = models.IntegerField(primary_key=True)
    uzytkownik_id = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='playlists')
    nazwa = models.CharField(max_length=100)


class PlaylistaUtwor(models.Model):
    class Meta:
        db_table = "playlista_utwor"
    playlista_id = models.ForeignKey(Playlista, on_delete=models.CASCADE, related_name='playlistSongs_playlists')
    utwor_id = models.ForeignKey(Utwor, on_delete=models.CASCADE, related_name='playlistSongs_songs')


class Subskrypcja(models.Model):
    class Meta:
        db_table = "subskrypcja"
    uzytkownik_id = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='subscriptions_user')
    autor_id = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='subscriptions_author')
