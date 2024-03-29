from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class Autor(models.Model):
    class Meta:
        db_table = "autor"

    AUTOR_TYPES = (
        ('ONE', 'osoba'),
        ('MUL', 'zespół')
    )

    autor_id = models.AutoField(primary_key=True)
    imie = models.CharField(max_length=30, null=True)
    nazwisko = models.CharField(max_length=50, null=True)
    pseudonim = models.CharField(max_length=40, null=True)
    rodzaj_autora = models.CharField(choices=AUTOR_TYPES, max_length=6, default='osoba')
    wiecej_info = models.TextField(null=True)

    def __str__(self):
        return self.pseudonim if self.pseudonim else f"{self.imie} {self.nazwisko}"

    @staticmethod
    def search(query):
        results = Autor.objects.filter(
            models.Q(imie__contains=query) |
            models.Q(nazwisko__contains=query) |
            models.Q(pseudonim__contains=query)
        )
        return results

    def get_subscribe_url(self):
        return reverse('music:like', args=['autor', self.autor_id])


class Album(models.Model):
    class Meta:
        db_table = "album"

    album_id = models.AutoField(primary_key=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='albums_by_autor')
    tytul = models.CharField(max_length=50)
    rok_wydania = models.SmallIntegerField()
    wiecej_info = models.TextField(null=True)

    def __str__(self):
        return f'"{self.tytul}" {self.autor}'

    @staticmethod
    def search(query):
        if query.isdigit():
            results = Album.objects.filter(rok_wydania__exact=query)
        else:
            results = Album.objects.filter(
                models.Q(tytul__contains=query) |
                models.Q(autor__imie__contains=query) |
                models.Q(autor__nazwisko__contains=query) |
                models.Q(autor__pseudonim__contains=query)
            )
        return results

    def get_like_url(self):
        return reverse('music:like', args=['album', self.album_id])


class Utwor(models.Model):
    class Meta:
        db_table = "utwor"

    utwor_id = models.AutoField(primary_key=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='songs_by_autor')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs_in_album')
    tytul = models.CharField(max_length=60)
    gatunek = models.CharField(max_length=30)
    tekst_sciezka = models.CharField(max_length=5000, default='')
    plik_sciezka = models.CharField(max_length=60)

    @staticmethod
    def search(query):
        results = Utwor.objects.filter(
            models.Q(tytul__contains=query) |
            models.Q(gatunek__contains=query) |
            models.Q(autor__imie__contains=query) |
            models.Q(autor__nazwisko__contains=query) |
            models.Q(autor__pseudonim__contains=query)
        )
        return results

    def get_text_url(self):
        return reverse('music:text', args=[self.utwor_id])

    def get_like_url(self):
        return reverse('music:like', args=['utwor', self.utwor_id])

    def get_play_url(self):
        return reverse('music:play', args=[self.plik_sciezka])

    def __str__(self):
        return f'"{self.tytul}" {self.autor}'


class Uzytkownik(AbstractUser):
    class Meta:
        db_table = "uzytkownik"

    ACCOUNTS_TYPES = (
        ('FR', 'free'),
        ('PR', 'premium')
    )

    account_type = models.CharField(choices=ACCOUNTS_TYPES, max_length=7, default='free')

    def __str__(self):
        return self.username


class Playlista(models.Model):
    class Meta:
        db_table = "playlista"

    playlista_id = models.IntegerField(primary_key=True)
    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='playlists')
    nazwa = models.CharField(max_length=100)

    def __str__(self):
        return f'"{self.nazwa}" {self.uzytkownik}'

    @staticmethod
    def search(query):
        results = Playlista.objects.filter(
            models.Q(nazwa__contains=query)
        )
        return results

    def get_like_url(self):
        return reverse('music:like', args=['playlista', self.playlista_id])


class BibliotekaPlaylist(models.Model):
    class Meta:
        db_table = "playlista_utwor"

    playlista = models.ForeignKey(Playlista, on_delete=models.CASCADE, related_name='songs_in_playlist')
    utwor = models.ForeignKey(Utwor, on_delete=models.CASCADE, related_name='playlists_with_song')

    def __str__(self):
        return str(self.utwor)

    def get_play_url(self):
        return reverse('music:play', args=[self.utwor.plik_sciezka])


class Subskrypcja(models.Model):
    class Meta:
        db_table = "subskrypcja"

    id = models.AutoField(primary_key=True)
    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='subscriptions_user')
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='subscriptions_author')

    def get_unsubscribe_url(self):
        return reverse('music:unlike', args=['autor', self.id])


class BibliotekaPiosenek(models.Model):
    class Meta:
        db_table = 'biblioteka_piosenki'

    id = models.AutoField(primary_key=True)
    utwor = models.ForeignKey(Utwor, on_delete=models.CASCADE, related_name='songs_in_library')
    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='user_songs_library')

    def get_download_url(self):
        return self.utwor.get_download_url()

    def get_play_url(self):
        return self.utwor.get_play_url()

    def get_unlike_url(self):
        return reverse('music:unlike', args=['utwor', self.id])

    def get_text_url(self):
        return self.utwor.get_text_url()


class BibliotekaAlbumow(models.Model):
    class Meta:
        db_table = 'biblioteka_albumy'

    id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='albums_in_library')
    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='user_albums_library')

    def get_unlike_url(self):
        return reverse('music:unlike', args=['album', self.id])

    def get_songs(self):
        return reverse('music:songs', args=['album', self.album_id])


class PlaylistyUzytkownika(models.Model):
    class Meta:
        db_table = 'biblioteka_playlisty'

    id = models.AutoField(primary_key=True)
    playlista = models.ForeignKey(Playlista, on_delete=models.CASCADE, related_name='playlists_in_library')
    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='user_playlists_library')

    def get_unlike_url(self):
        return reverse('music:unlike', args=['playlista', self.id])

    def get_songs(self):
        return reverse('music:songs', args=['playlista', self.playlista_id])
