---
name: add-endpoint
description: Use this skill to add a new endpoint to the Apka-muzyczna Django project. Triggers include phrases like "dodaj endpoint", "dodaj feature", "zaimplementuj", "stwórz widok", "dodaj funkcjonalność", "add endpoint", "add feature". Creates the view, URL, template, optional form, tests, and FEATURES.md entry in one go.
---

Dodaj nowy endpoint do aplikacji Django **Apka-muzyczna** na podstawie opisu: **$ARGUMENTS**

## Instrukcja

Przed implementacją przeczytaj kolejno:
1. `music/views.py` — poznaj styl istniejących widoków (dekoratory, ORM, messages, redirect)
2. `music/urls.py` — poznaj konwencję nazewnictwa URL i `app_name = 'music'`
3. `music/models.py` — sprawdź dostępne modele i relacje
4. `music/forms.py` — sprawdź istniejące formularze; dołącz nowy tylko jeśli potrzebny
5. `music/tests.py` — poznaj styl testów (`pytest`, helper `login_user`, `@pytest.mark.django_db`)
6. `FEATURES.md` — znajdź ostatni numer funkcji, żeby przypisać kolejny

Następnie zaimplementuj endpoint krok po kroku:

### 1. Widok (`music/views.py`)
- Dopisz widok na końcu pliku
- Użyj `@login_required` jeśli endpoint wymaga autoryzacji
- Używaj wyłącznie Django ORM — bez raw SQL
- Używaj `messages.success / info / error` do komunikatów dla użytkownika
- Nazewnictwo: `snake_case`; zmienne opisowe po polsku lub angielsku (zgodnie z resztą kodu)
- Jeśli widok obsługuje formularz: `GET` renderuje formularz, `POST` go przetwarza

### 2. URL (`music/urls.py`)
- Dopisz `path(...)` do listy `urlpatterns`
- Nadaj znaczącą nazwę (`name=`), spójną z istniejącymi (np. `name='rate_song'`)

### 3. Szablon (`music/templates/<nazwa>.html`)
- Dziedzicz z `start.html`: `{% extends 'start.html' %}`
- Stosuj dark-theme i W3.CSS (klasy `w3-button`, `w3-panel`, `w3-card` itp.)
- Wyświetlaj messages jeśli są (blok `{% if messages %}` jest już w `start.html` — nie duplikuj)
- Przyciski "Wróć" linkuj przez `{% url 'music:...' %}`
- Trzymaj się stylu i struktury istniejących szablonów (np. `profile.html`, `history.html`)

### 4. Formularz (`music/forms.py`) — tylko jeśli potrzebny
- Dopisz klasę formularza dziedziczącą po `forms.Form` lub `forms.ModelForm`
- Doimportuj w `views.py`

### 5. Testy (`music/tests.py`)
- Napisz minimum 2 testy: happy path + edge case (np. brak autoryzacji, duplikat, brak rekordu)
- Używaj helpera `login_user(client, django_user_model, ...)`
- Dekoruj `@pytest.mark.django_db` tam gdzie dotykasz bazy

### 6. Aktualizacja `FEATURES.md`
- Znajdź odpowiednią sekcję tabeli (lub utwórz nową, jeśli nie pasuje do żadnej)
- Dopisz wiersz z kolejnym numerem, nazwą feature, statusem `[x]` i endpointem
- Zachowaj format Markdown identyczny z resztą pliku

Po implementacji uruchom testy, żeby upewnić się że nie ma regresji:
```
docker compose run --rm web pytest
```
Jeśli testy nie przejdą — napraw problem zanim zgłosisz zadanie jako ukończone.
