# Muza na luzie

Aplikacja muzyczna zbudowana w Django — strumieniowanie MP3, biblioteka ulubionych, playlisty i wyszukiwarka.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-4.1-green)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)
![Tests](https://img.shields.io/badge/tests-pytest-yellow)

---

## Funkcjonalności

- **Odtwarzanie** — strumieniowanie MP3 w przeglądarce, losowe odtwarzanie polubionych, historia odsłuchań
- **Wyszukiwanie** — pełnotekstowe przeszukiwanie piosenek, artystów, albumów i playlist
- **Biblioteka** — polubione piosenki, albumy i playlisty; subskrypcje artystów
- **Upload** — dodawanie plików MP3 z metadanymi; auto-tworzenie artysty i albumu; upload tekstów piosenek
- **Playlisty** — tworzenie playlist i dodawanie do nich piosenek
- **Rekomendacje** — propozycje oparte o polubienia i subskrypcje
- **Konto** — rejestracja, logowanie, reset hasła przez e-mail, ustawienia profilu, plan free/premium

---

## Stack technologiczny

| Warstwa       | Technologia                          |
|---------------|--------------------------------------|
| Backend       | Python 3.12, Django 4.1.5            |
| Baza danych   | SQLite                               |
| Formularze    | django-crispy-forms 1.14.0           |
| Testy         | pytest 7.2.1, pytest-django 4.5.2    |
| Konfiguracja  | python-dotenv 0.21.0                 |
| Konteneryzacja| Docker, docker-compose               |

---

## Szybki start

### Docker (zalecane)

```bash
docker compose up --build
```

Aplikacja będzie dostępna pod adresem `http://localhost:8000`.
Migracje uruchamiają się automatycznie przy starcie kontenera.

### Lokalnie

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Konfiguracja `.env`

Utwórz plik `.env` w katalogu głównym projektu:

| Zmienna               | Opis                              | Domyślnie              |
|-----------------------|-----------------------------------|------------------------|
| `SECRET_KEY`          | Klucz Django                      | wartość deweloperska   |
| `EMAIL_BACKEND`       | Backend poczty                    | `console`              |
| `EMAIL_HOST`          | Serwer SMTP                       | —                      |
| `EMAIL_PORT`          | Port SMTP                         | —                      |
| `EMAIL_HOST_USER`     | Adres e-mail nadawcy              | —                      |
| `EMAIL_HOST_PASSWORD` | Hasło do konta pocztowego         | —                      |
| `DEFAULT_FROM_EMAIL`  | Adres „From" w wysyłanych mailach | `noreply@muzanaluzie.pl`|

---

## Testy

```bash
docker compose run --rm web pytest
```

---

## Struktura projektu

```
Apka-muzyczna/
├── Apka_muzyczna/   # Konfiguracja projektu (settings, urls, wsgi)
├── music/           # Główna aplikacja
│   ├── models.py    # Modele danych
│   ├── views.py     # Logika biznesowa
│   ├── urls.py      # Routing
│   ├── forms.py     # Formularze
│   ├── tests.py     # Testy
│   └── templates/   # Szablony HTML
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── FEATURES.md      # Szczegółowa lista funkcjonalności
```

---

Stworzył [@Marcin-Ramotowski](https://github.com/Marcin-Ramotowski) — zainspirowany serwisem YouTube Music.

Podziękowania dla Barbary Szema za wsparcie okazane podczas realizacji projektu.
