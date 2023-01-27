from django.test import Client
from django.shortcuts import reverse
import pytest
from .models import Autor


def test_start_run():
    client = Client()
    response = client.get('/')
    assert response.status_code == 200


def test_login_run():
    client = Client()
    response = client.get('/login')
    assert response.status_code == 301


def test_logout_run():
    client = Client()
    response = client.get('/logout')
    assert response.status_code == 301


def test_profile_run():
    client = Client()
    response = client.get('/profile')
    assert response.status_code == 301


def test_search_run():
    client = Client()
    response = client.get('/search')
    assert response.status_code == 301


def test_download_run():
    client = Client()
    response = client.get('/download')
    assert response.status_code == 301


def test_upload_run():
    client = Client()
    response = client.get('/login')
    assert response.status_code == 301


def test_start_content_when_not_login():
    """ Sprawdza czy uzytkownik widzi właściwą treść na stronie, gdy nie jest zalogowany"""
    client = Client()
    response = client.get('/')
    check_content_when_not_login = b'Aby rozpocz\xc4\x85\xc4\x87 przygod\xc4\x99,' \
                                   b' zaloguj si\xc4\x99' in response.content
    assert check_content_when_not_login


@pytest.mark.django_db
def test_search_autor():
    client = Client()
    response = client.get('/search')

    database = Autor
    query = 'Natalia'
    results = database.objects.filter(imie=query)
    # results = results.values_list(*fields)
    assert results.first() is not None
