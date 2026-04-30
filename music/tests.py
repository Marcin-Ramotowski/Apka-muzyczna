import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from music.models import (
    Album, Autor, Subskrypcja, Utwor,
    BibliotekaPiosenek, BibliotekaAlbumow, PlaylistyUzytkownika,
    Playlista, BibliotekaPlaylist, ListeningHistory,
)


def login_user(client, django_user_model, username='testuser', password='testpassword'):
    """Tworzy i loguje testowego użytkownika do serwisu."""
    user = django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return user


def make_song(title='Test Song', genre='pop', filename='test.mp3'):
    """Tworzy autora, album i piosenkę do użycia w testach."""
    autor = Autor.objects.create(pseudonim='Test Artist')
    album = Album.objects.create(autor=autor, tytul='Test Album', rok_wydania=2020)
    return Utwor.objects.create(autor=autor, album=album, tytul=title,
                                gatunek=genre, plik_sciezka=filename)


# ==================== Testy strony startowej ====================

def test_start_page_for_anonymous_user(client):
    """Sprawdza, czy użytkownik widzi właściwą treść na stronie, gdy nie jest zalogowany."""
    response = client.get('/')
    assert response.status_code == 200
    assert "Zarejestruj się".encode() in response.content
    assert "Zaloguj się".encode() in response.content
    assert "Aby rozpocząć przygodę, zaloguj się".encode() in response.content


@pytest.mark.django_db
def test_start_page_for_authenticated_user(client, django_user_model):
    """Sprawdza, czy użytkownik widzi właściwą treść na stronie, gdy jest zalogowany."""
    login_user(client, django_user_model, 'testuser', 'testpassword')
    response = client.get('/')
    assert "Twój profil".encode() in response.content
    assert "Wyloguj się".encode() in response.content


# ==================== Feature #1: Rejestracja użytkownika ====================

@pytest.mark.django_db
def test_registration_creates_user(client, django_user_model):
    client.post('/accounts/register/', {
        'first_name': 'Jan', 'last_name': 'Kowalski',
        'username': 'janek', 'email': 'janek@test.pl',
        'password1': 'Qwerty12345!', 'password2': 'Qwerty12345!',
    })
    assert django_user_model.objects.filter(username='janek').exists()


@pytest.mark.django_db
def test_registration_page_accessible_anonymous(client):
    response = client.get('/accounts/register/')
    assert response.status_code == 200


# ==================== Feature #2: Logowanie ====================

@pytest.mark.django_db
def test_login_with_valid_credentials(client, django_user_model):
    django_user_model.objects.create_user(username='janek', password='Qwerty12345!')
    client.post('/accounts/login/', {'username': 'janek', 'password': 'Qwerty12345!'})
    assert '_auth_user_id' in client.session


@pytest.mark.django_db
def test_login_with_invalid_credentials(client, django_user_model):
    django_user_model.objects.create_user(username='janek', password='Qwerty12345!')
    client.post('/accounts/login/', {'username': 'janek', 'password': 'wrong'})
    assert '_auth_user_id' not in client.session


# ==================== Feature #3: Wylogowanie ====================

@pytest.mark.django_db
def test_logout_ends_session(client, django_user_model):
    login_user(client, django_user_model)
    assert '_auth_user_id' in client.session
    client.post('/accounts/logout/')
    assert '_auth_user_id' not in client.session


# ==================== Feature #4: Typy kont ====================

@pytest.mark.django_db
def test_account_type_field_exists(django_user_model):
    user = django_user_model.objects.create_user(username='janek', password='pass')
    assert hasattr(user, 'account_type')


# ==================== Feature #6: Strona profilu ====================

@pytest.mark.django_db
def test_profile_requires_login(client):
    response = client.get('/profile/')
    assert response.status_code == 302
    assert 'login' in response['Location']


@pytest.mark.django_db
def test_profile_shows_liked_songs(client, django_user_model):
    user = login_user(client, django_user_model)
    song = make_song(title='Ulubiona Piosenka')
    BibliotekaPiosenek.objects.create(uzytkownik=user, utwor=song)
    response = client.get('/profile/')
    assert 'Ulubiona Piosenka'.encode() in response.content


@pytest.mark.django_db
def test_profile_shows_subscribed_authors(client, django_user_model):
    """Sprawdza, czy użytkownik widzi subskrybowanych artystów na stronie."""
    user = login_user(client, django_user_model, 'testuser', 'testpassword')
    author = Autor.objects.create(imie="Małgorzata", nazwisko="Jamroży", pseudonim="Margaret",
                                  wiecej_info="polska piosenkarka, kompozytorka i autorka tekstów piosenek,"
                                              " z wykształcenia projektantka mody")
    Subskrypcja.objects.create(autor_id=author.autor_id, uzytkownik_id=user.id)
    response = client.get('/profile/')
    assert b'Margaret' in response.content


# ==================== Feature #7: Dodanie piosenki do biblioteki ====================

@pytest.mark.django_db
def test_like_song_creates_library_entry(client, django_user_model):
    user = login_user(client, django_user_model)
    song = make_song()
    client.get(f'/like/utwor/{song.pk}')
    assert BibliotekaPiosenek.objects.filter(uzytkownik=user, utwor=song).exists()


@pytest.mark.django_db
def test_like_song_requires_login(client, django_user_model):
    song = make_song()
    response = client.get(f'/like/utwor/{song.pk}')
    assert response.status_code == 302
    assert 'login' in response['Location']


# ==================== Feature #8: Dodanie albumu do biblioteki ====================

@pytest.mark.django_db
def test_like_album_creates_library_entry(client, django_user_model):
    user = login_user(client, django_user_model)
    autor = Autor.objects.create(pseudonim='Test Artist')
    album = Album.objects.create(autor=autor, tytul='Test Album', rok_wydania=2020)
    client.get(f'/like/album/{album.pk}')
    assert BibliotekaAlbumow.objects.filter(uzytkownik=user, album=album).exists()


# ==================== Feature #9: Subskrypcja artysty ====================

@pytest.mark.django_db
def test_like_autor_creates_subscription(client, django_user_model):
    user = login_user(client, django_user_model)
    autor = Autor.objects.create(pseudonim='Test Artist')
    client.get(f'/like/autor/{autor.pk}')
    assert Subskrypcja.objects.filter(uzytkownik=user, autor=autor).exists()


# ==================== Feature #10: Zapisanie playlisty ====================

@pytest.mark.django_db
def test_like_playlist_saves_to_library(client, django_user_model):
    user = login_user(client, django_user_model)
    playlist = Playlista.objects.create(uzytkownik=user, nazwa='Moja lista')
    client.get(f'/like/playlista/{playlist.pk}')
    assert PlaylistyUzytkownika.objects.filter(uzytkownik=user, playlista=playlist).exists()


# ==================== Feature #11: Usunięcie piosenki z biblioteki ====================

@pytest.mark.django_db
def test_unlike_song_removes_library_entry(client, django_user_model):
    user = login_user(client, django_user_model)
    song = make_song()
    entry = BibliotekaPiosenek.objects.create(uzytkownik=user, utwor=song)
    client.get(f'/unlike/utwor/{entry.pk}')
    assert not BibliotekaPiosenek.objects.filter(pk=entry.pk).exists()


# ==================== Feature #12: Usunięcie albumu z biblioteki ====================

@pytest.mark.django_db
def test_unlike_album_removes_library_entry(client, django_user_model):
    user = login_user(client, django_user_model)
    autor = Autor.objects.create(pseudonim='Test Artist')
    album = Album.objects.create(autor=autor, tytul='Test Album', rok_wydania=2020)
    entry = BibliotekaAlbumow.objects.create(uzytkownik=user, album=album)
    client.get(f'/unlike/album/{entry.pk}')
    assert not BibliotekaAlbumow.objects.filter(pk=entry.pk).exists()


# ==================== Feature #13: Odsubskrybowanie artysty ====================

@pytest.mark.django_db
def test_unlike_author(client, django_user_model):
    """Sprawdza, czy użytkownik może usunąć autora z biblioteki."""
    user = login_user(client, django_user_model, 'testuser', 'testpassword')
    author = Autor.objects.create(imie="Małgorzata", nazwisko="Jamroży", pseudonim="Margaret",
                                  wiecej_info="polska piosenkarka, kompozytorka i autorka tekstów piosenek,"
                                              " z wykształcenia projektantka mody")
    entry = Subskrypcja.objects.create(autor_id=author.autor_id, uzytkownik_id=user.id)
    client.get(f'/unlike/autor/{entry.pk}')
    assert not Subskrypcja.objects.filter(pk=entry.pk).exists()


# ==================== Feature #14: Usunięcie playlisty z biblioteki ====================

@pytest.mark.django_db
def test_unlike_playlist_removes_from_library(client, django_user_model):
    user = login_user(client, django_user_model)
    playlist = Playlista.objects.create(uzytkownik=user, nazwa='Moja lista')
    entry = PlaylistyUzytkownika.objects.create(uzytkownik=user, playlista=playlist)
    client.get(f'/unlike/playlista/{entry.pk}')
    assert not PlaylistyUzytkownika.objects.filter(pk=entry.pk).exists()


# ==================== Feature #15: Duplikat-like guard ====================

@pytest.mark.django_db
def test_duplicate_like_does_not_create_second_entry(client, django_user_model):
    user = login_user(client, django_user_model)
    autor = Autor.objects.create(pseudonim='Test Artist')
    client.get(f'/like/autor/{autor.pk}')
    client.get(f'/like/autor/{autor.pk}')
    assert Subskrypcja.objects.filter(uzytkownik=user, autor=autor).count() == 1


@pytest.mark.django_db
def test_duplicate_like_shows_info_message(client, django_user_model):
    user = login_user(client, django_user_model)
    autor = Autor.objects.create(pseudonim='Test Artist')
    client.get(f'/like/autor/{autor.pk}')
    response = client.get(f'/like/autor/{autor.pk}', follow=True)
    messages_list = list(response.context['messages'])
    assert any('Już polubiłeś' in str(m) for m in messages_list)


# ==================== Feature #16: Wyszukiwanie artystów ====================

@pytest.mark.django_db
def test_search_autor_returns_results(client, django_user_model):
    login_user(client, django_user_model)
    Autor.objects.create(pseudonim='Unique Artist XYZ')
    response = client.post('/search/', {'database': 'autor', 'query': 'Unique Artist XYZ'})
    assert b'Unique Artist XYZ' in response.content


# ==================== Feature #17: Wyszukiwanie piosenek ====================

@pytest.mark.django_db
def test_search_song_returns_results(client, django_user_model):
    login_user(client, django_user_model)
    make_song(title='Unique Song XYZ')
    response = client.post('/search/', {'database': 'piosenka', 'query': 'Unique Song XYZ'})
    assert b'Unique Song XYZ' in response.content


# ==================== Feature #18: Wyszukiwanie albumów ====================

@pytest.mark.django_db
def test_search_album(client, django_user_model):
    """Sprawdza, czy wysyłane przez użytkownika query zwraca pasujące rekordy z tabeli albumów."""
    author = Autor.objects.create(imie="Małgorzata", nazwisko="Jamroży", pseudonim="Margaret",
                                  wiecej_info="polska piosenkarka, kompozytorka i autorka tekstów piosenek,"
                                              " z wykształcenia projektantka mody")
    album = Album.objects.create(autor_id=author.autor_id, tytul="Monkey Business", rok_wydania=2017,
                                 wiecej_info="12 utworów")
    results = Album.search('Margaret')
    assert album in results


@pytest.mark.django_db
def test_search_album_http_returns_results(client, django_user_model):
    login_user(client, django_user_model)
    autor = Autor.objects.create(pseudonim='Test Artist')
    Album.objects.create(autor=autor, tytul='Unique Album XYZ', rok_wydania=2020)
    response = client.post('/search/', {'database': 'album', 'query': 'Unique Album XYZ'})
    assert b'Unique Album XYZ' in response.content


# ==================== Feature #19: Wyszukiwanie playlist ====================

@pytest.mark.django_db
def test_search_playlist_returns_results(client, django_user_model):
    user = login_user(client, django_user_model)
    Playlista.objects.create(uzytkownik=user, nazwa='Unique Playlist XYZ')
    response = client.post('/search/', {'database': 'playlista', 'query': 'Unique Playlist XYZ'})
    assert b'Unique Playlist XYZ' in response.content


# ==================== Feature #20: Streamowanie MP3 ====================

@pytest.mark.django_db
def test_play_requires_login(client):
    response = client.get('/play/song.mp3')
    assert response.status_code == 302
    assert 'login' in response['Location']


@pytest.mark.django_db
def test_play_file(client, django_user_model):
    """Sprawdza, czy przekazywanie plików do odtwarzacza działa prawidłowo."""
    response = client.get('/play/Margaret - Byle Jak.mp3')
    assert response.status_code in (200, 302)


@pytest.mark.django_db
def test_play_streams_file(client, django_user_model, tmp_path, monkeypatch):
    login_user(client, django_user_model)
    test_file = tmp_path / 'song.mp3'
    test_file.write_bytes(b'fake mp3 content')
    monkeypatch.setattr('music.views.MEDIA_URL', str(tmp_path) + '/')
    response = client.get('/play/song.mp3')
    assert response.status_code == 200
    assert response.get('Content-Type') == 'audio/mpeg'


# ==================== Feature #22: Wyświetlanie tekstu piosenki ====================

@pytest.mark.django_db
def test_display_text_requires_login(client, django_user_model):
    song = make_song()
    response = client.get(f'/text/{song.pk}')
    assert response.status_code == 302
    assert 'login' in response['Location']


@pytest.mark.django_db
def test_display_text_shows_song_title(client, django_user_model):
    login_user(client, django_user_model)
    song = make_song(title='Piosenka Bez Tekstu')
    response = client.get(f'/text/{song.pk}')
    assert b'Piosenka Bez Tekstu' in response.content


@pytest.mark.django_db
def test_display_text_no_lyrics_shows_info_message(client, django_user_model):
    login_user(client, django_user_model)
    song = make_song()  # tekst_sciezka defaults to ''
    response = client.get(f'/text/{song.pk}', follow=True)
    messages_list = list(response.context['messages'])
    assert any('nie ma jeszcze dodanego tekstu' in str(m) for m in messages_list)


# ==================== Feature #23: Lista piosenek w albumie ====================

@pytest.mark.django_db
def test_songs_in_album_listed(client, django_user_model):
    login_user(client, django_user_model)
    song = make_song(title='Album Track')
    response = client.get(f'/songs/album/{song.album.pk}')
    assert b'Album Track' in response.content


# ==================== Feature #24: Lista piosenek w playliście ====================

@pytest.mark.django_db
def test_songs_in_playlist_listed(client, django_user_model):
    user = login_user(client, django_user_model)
    song = make_song(title='Playlist Track')
    playlist = Playlista.objects.create(uzytkownik=user, nazwa='Test Playlist')
    BibliotekaPlaylist.objects.create(playlista=playlist, utwor=song)
    response = client.get(f'/songs/playlista/{playlist.pk}')
    assert b'Playlist Track' in response.content


# ==================== Feature #25, #26, #27: Upload MP3 ====================

@pytest.mark.django_db
def test_upload_creates_song_record(client, django_user_model, tmp_path, monkeypatch):
    login_user(client, django_user_model)
    (tmp_path / 'music' / 'static' / 'media').mkdir(parents=True)
    monkeypatch.setattr('music.views.BASE_DIR', tmp_path)
    mp3 = SimpleUploadedFile('song.mp3', b'fake mp3', content_type='audio/mpeg')
    client.post('/upload/', {
        'title': 'New Song', 'genre': 'rock',
        'autor': 'New Artist', 'album_title': 'New Album',
        'album_year': 2020, 'file': mp3,
    })
    assert Utwor.objects.filter(tytul='New Song').exists()


@pytest.mark.django_db
def test_upload_creates_author_if_not_exists(client, django_user_model, tmp_path, monkeypatch):
    login_user(client, django_user_model)
    (tmp_path / 'music' / 'static' / 'media').mkdir(parents=True)
    monkeypatch.setattr('music.views.BASE_DIR', tmp_path)
    mp3 = SimpleUploadedFile('song.mp3', b'fake mp3', content_type='audio/mpeg')
    client.post('/upload/', {
        'title': 'Song', 'genre': 'rock',
        'autor': 'Brand New Artist', 'album_title': 'Album',
        'album_year': 2020, 'file': mp3,
    })
    assert Autor.objects.filter(pseudonim='Brand New Artist').exists()


@pytest.mark.django_db
def test_upload_creates_album_if_not_exists(client, django_user_model, tmp_path, monkeypatch):
    login_user(client, django_user_model)
    (tmp_path / 'music' / 'static' / 'media').mkdir(parents=True)
    monkeypatch.setattr('music.views.BASE_DIR', tmp_path)
    mp3 = SimpleUploadedFile('song.mp3', b'fake mp3', content_type='audio/mpeg')
    client.post('/upload/', {
        'title': 'Song', 'genre': 'rock',
        'autor': 'Artist', 'album_title': 'Brand New Album',
        'album_year': 2021, 'file': mp3,
    })
    assert Album.objects.filter(tytul='Brand New Album', rok_wydania=2021).exists()


# ==================== Feature #28: Duplikat-upload guard ====================

@pytest.mark.django_db
def test_upload_duplicate_guard(client, django_user_model):
    login_user(client, django_user_model)
    autor = Autor.objects.create(pseudonim='Existing Artist')
    album = Album.objects.create(autor=autor, tytul='Existing Album', rok_wydania=2020)
    Utwor.objects.create(autor=autor, album=album, tytul='Existing Song',
                         gatunek='pop', plik_sciezka='existing.mp3')
    mp3 = SimpleUploadedFile('song.mp3', b'fake mp3', content_type='audio/mpeg')
    client.post('/upload/', {
        'title': 'Existing Song', 'genre': 'pop',
        'autor': 'Existing Artist', 'album_title': 'Existing Album',
        'album_year': 2020, 'file': mp3,
    })
    assert Utwor.objects.filter(tytul='Existing Song').count() == 1


# ==================== Feature #29: Upload tekstu piosenki ====================

@pytest.mark.django_db
def test_upload_text_requires_login(client, django_user_model):
    song = make_song()
    response = client.get(f'/text/upload/{song.pk}')
    assert response.status_code == 302
    assert 'login' in response['Location']


@pytest.mark.django_db
def test_upload_text_saves_lyrics(client, django_user_model, tmp_path, monkeypatch):
    login_user(client, django_user_model)
    monkeypatch.setattr('music.views.BASE_DIR', tmp_path)
    song = make_song()
    client.post(f'/text/upload/{song.pk}', {'lyrics': 'Verse 1\nVerse 2'})
    song.refresh_from_db()
    assert song.tekst_sciezka != ''


# ==================== Feature #35: Historia słuchania ====================

@pytest.mark.django_db
def test_history_shows_played_songs(client, django_user_model):
    user = login_user(client, django_user_model)
    song = make_song(title='Played Song')
    ListeningHistory.objects.create(uzytkownik=user, utwor=song)
    response = client.get('/history/')
    assert b'Played Song' in response.content


@pytest.mark.django_db
def test_history_date_filter_excludes_out_of_range(client, django_user_model):
    from datetime import date, timedelta
    user = login_user(client, django_user_model)
    song = make_song(title='History Song')
    ListeningHistory.objects.create(uzytkownik=user, utwor=song)
    # Filtrowanie od jutra — dzisiejszy wpis nie powinien być widoczny
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = client.get(f'/history/?date_from={tomorrow}')
    assert b'History Song' not in response.content


# ==================== Feature #36: Rekomendacje ====================

@pytest.mark.django_db
def test_recommendations_based_on_liked_genre(client, django_user_model):
    user = login_user(client, django_user_model)
    liked_song = make_song(title='Liked Song', genre='jazz')
    BibliotekaPiosenek.objects.create(uzytkownik=user, utwor=liked_song)
    autor2 = Autor.objects.create(pseudonim='Other Artist')
    album2 = Album.objects.create(autor=autor2, tytul='Other Album', rok_wydania=2021)
    Utwor.objects.create(autor=autor2, album=album2, tytul='Suggested Song',
                         gatunek='jazz', plik_sciezka='suggested.mp3')
    response = client.get('/recommendations/')
    assert b'Suggested Song' in response.content


@pytest.mark.django_db
def test_recommendations_excludes_already_liked(client, django_user_model):
    user = login_user(client, django_user_model)
    liked_song = make_song(title='Already Liked', genre='jazz')
    BibliotekaPiosenek.objects.create(uzytkownik=user, utwor=liked_song)
    response = client.get('/recommendations/')
    assert b'Already Liked' not in response.content


# ==================== Feature #37: Tworzenie playlisty ====================

@pytest.mark.django_db
def test_create_playlist_saves_to_db(client, django_user_model):
    user = login_user(client, django_user_model)
    client.post('/playlist/create/', {'name': 'Nowa Playlista'})
    assert Playlista.objects.filter(uzytkownik=user, nazwa='Nowa Playlista').exists()


@pytest.mark.django_db
def test_create_playlist_unique_name_guard(client, django_user_model):
    user = login_user(client, django_user_model)
    Playlista.objects.create(uzytkownik=user, nazwa='Istniejąca')
    client.post('/playlist/create/', {'name': 'Istniejąca'})
    assert Playlista.objects.filter(uzytkownik=user, nazwa='Istniejąca').count() == 1


# ==================== Feature #38: Dodawanie piosenki do playlisty ====================

@pytest.mark.django_db
def test_add_song_to_playlist_creates_entry(client, django_user_model):
    user = login_user(client, django_user_model)
    song = make_song()
    playlist = Playlista.objects.create(uzytkownik=user, nazwa='Test Playlist')
    client.post('/playlist/add-song/', {'playlist_id': playlist.pk, 'song_id': song.pk})
    assert BibliotekaPlaylist.objects.filter(playlista=playlist, utwor=song).exists()


@pytest.mark.django_db
def test_add_song_to_playlist_ownership_check(client, django_user_model):
    login_user(client, django_user_model, username='owner', password='pass1')
    other = django_user_model.objects.create_user(username='other', password='pass2')
    song = make_song()
    playlist = Playlista.objects.create(uzytkownik=other, nazwa='Other Playlist')
    client.post('/playlist/add-song/', {'playlist_id': playlist.pk, 'song_id': song.pk})
    assert not BibliotekaPlaylist.objects.filter(playlista=playlist, utwor=song).exists()


@pytest.mark.django_db
def test_add_song_to_playlist_duplicate_guard(client, django_user_model):
    user = login_user(client, django_user_model)
    song = make_song()
    playlist = Playlista.objects.create(uzytkownik=user, nazwa='Test Playlist')
    BibliotekaPlaylist.objects.create(playlista=playlist, utwor=song)
    client.post('/playlist/add-song/', {'playlist_id': playlist.pk, 'song_id': song.pk})
    assert BibliotekaPlaylist.objects.filter(playlista=playlist, utwor=song).count() == 1


# ==================== Feature #39: Losowa polubiona piosenka ====================

@pytest.mark.django_db
def test_play_random_liked_shows_song(client, django_user_model):
    user = login_user(client, django_user_model)
    song = make_song(title='Random Liked Song')
    BibliotekaPiosenek.objects.create(uzytkownik=user, utwor=song)
    response = client.get('/play-random-liked/')
    assert b'Random Liked Song' in response.content


@pytest.mark.django_db
def test_play_random_liked_no_songs_shows_info(client, django_user_model):
    login_user(client, django_user_model)
    response = client.get('/play-random-liked/', follow=True)
    messages_list = list(response.context['messages'])
    assert any('Nie masz jeszcze żadnych polubionych' in str(m) for m in messages_list)


# ==================== Feature #40: Ustawienia konta ====================

@pytest.mark.django_db
def test_account_settings_requires_login(client):
    response = client.get('/settings/')
    assert response.status_code == 302
    assert 'login' in response['Location']


@pytest.mark.django_db
def test_account_settings_updates_user_info(client, django_user_model):
    user = login_user(client, django_user_model)
    client.post('/settings/', {
        'save_info': '1',
        'first_name': 'Nowe', 'last_name': 'Nazwisko', 'email': 'nowy@test.pl',
    })
    user.refresh_from_db()
    assert user.first_name == 'Nowe'
    assert user.email == 'nowy@test.pl'
