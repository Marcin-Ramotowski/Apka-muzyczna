import pytest
from music.models import Album, Autor, Subskrypcja


def login_user(client, django_user_model, username, password):
    """ Tworzy i loguje testowego użytkownika do serwisu."""
    user = django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return user


def test_start_page_for_anonymous_user(client):
    """ Sprawdza, czy użytkownik widzi właściwą treść na stronie, gdy nie jest zalogowany."""
    response = client.get('/')
    assert response.status_code == 200
    assert "Zarejestruj się".encode() in response.content
    assert "Zaloguj się".encode() in response.content
    assert "Aby rozpocząć przygodę, zaloguj się".encode() in response.content


@pytest.mark.django_db
def test_start_page_for_authenticated_user(client, django_user_model):
    """ Sprawdza, czy użytkownik widzi właściwą treść na stronie, gdy jest zalogowany."""
    login_user(client, django_user_model, 'testuser', 'testpassword')
    response = client.get('/')
    assert "Twój profil".encode() in response.content
    assert "Wyloguj się".encode() in response.content


@pytest.mark.django_db
def test_artists_on_user_profile(client, django_user_model):
    """ Sprawdza, czy użytkownik widzi subskrybowanych artystów na stronie."""
    user = login_user(client, django_user_model, 'testuser', 'testpassword')
    author = Autor.objects.create(imie="Małgorzata", nazwisko="Jamroży", pseudonim="Margaret",
                                  wiecej_info="polska piosenkarka, kompozytorka i autorka tekstów piosenek,"
                                              " z wykształcenia projektantka mody")
    Subskrypcja.objects.create(autor_id=author.autor_id, uzytkownik_id=user.id)
    response = client.get('/profile/')
    assert b'Margaret' in response.content


@pytest.mark.django_db
def test_search_album(client, django_user_model):
    """ Sprawdza, czy wysyłane przez użytkownika query zwraca pasujące rekordy z tabeli albumów."""
    author = Autor.objects.create(imie="Małgorzata", nazwisko="Jamroży", pseudonim="Margaret",
                                  wiecej_info="polska piosenkarka, kompozytorka i autorka tekstów piosenek,"
                                              " z wykształcenia projektantka mody")
    album = Album.objects.create(autor_id=author.autor_id, tytul="Monkey Business", rok_wydania=2017,
                                 wiecej_info="12 utworów")
    model = Album
    query = 'Margaret'
    results = model.search(query)
    assert album in results


@pytest.mark.django_db
def test_unlike_author(client, django_user_model):
    """ Sprawdza, czy użytkownik może usunąć autora z biblioteki."""
    user = login_user(client, django_user_model, 'testuser', 'testpassword')
    author = Autor.objects.create(imie="Małgorzata", nazwisko="Jamroży", pseudonim="Margaret",
                                  wiecej_info="polska piosenkarka, kompozytorka i autorka tekstów piosenek,"
                                              " z wykształcenia projektantka mody")
    Subskrypcja.objects.create(autor_id=author.autor_id, uzytkownik_id=user.id)
    response = client.get('/unlike/autor/1')
    assert response.status_code in (200, 302)

@pytest.mark.django_db
def test_play_file(client, django_user_model):
    """ Sprawdza, czy przekazywanie plików do odtwarzacza działa prawidłowo."""
    response = client.get('/play/Margaret - Byle Jak.mp3')
    assert response.status_code in (200, 302)
