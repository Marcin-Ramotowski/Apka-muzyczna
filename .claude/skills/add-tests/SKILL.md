---
name: add-tests
description: Use this skill to write tests for features listed in FEATURES.md that lack test coverage. Triggers include phrases like "dodaj testy", "napisz testy", "pokryj testami", "brakuje testów", "add tests", "write tests", "test coverage". Accepts optional feature numbers as arguments (e.g. "7 8 9") to target specific features; without arguments processes all implemented [x] features.
---

Dopisz testy do `music/tests.py` dla projektu **Apka-muzyczna** tak, aby każda funkcja oznaczona `[x]` w `FEATURES.md` była potwierdzona co najmniej jednym testem. Jeśli podano argumenty (`$ARGUMENTS`), ogranicz się do feature'ów o podanych numerach (np. `7 8 9`); bez argumentów przetwórz wszystkie.

## Krok 1 — Zbierz bazę wiedzy

Przeczytaj wszystkie poniższe pliki (nie pomijaj żadnego):
- `FEATURES.md` — lista feature'ów z numerami i statusami
- `music/tests.py` — istniejące testy (sprawdź co już jest pokryte)
- `music/views.py` — implementacja widoków
- `music/urls.py` — ścieżki URL
- `music/models.py` — modele danych
- `music/forms.py` — formularze

## Krok 2 — Zmapuj istniejące testy do feature'ów

Dla każdego istniejącego testu ustal, który feature (numer z FEATURES.md) pokrywa. Test pokrywa feature jeśli:
- uderza w jego endpoint ORAZ
- weryfikuje efekt uboczny charakterystyczny dla tego feature (nie tylko kod HTTP)

Sporządź wewnętrzną listę: `{numer_feature: [lista_testów]}`. Feature bez żadnego testu na tej liście = **niepokryty**.

## Krok 3 — Napisz brakujące testy

Dla każdego niepokrytego (lub słabo pokrytego) feature'u z `[x]` napisz testy według poniższych zasad.

### Zasady obowiązkowe

**A. Jeden blok komentarza na feature:**
```python
# --- Feature #<nr>: <skrócona nazwa> ---
```
Umieszczaj go bezpośrednio nad pierwszym testem danego feature'u. Dzięki temu wiadomo, który test co pokrywa.

**B. Minimum jeden test happy-path:**
Test musi weryfikować efekt działania feature, nie tylko to że serwer odpowiedział.
- Dla akcji zmieniających bazę: sprawdź że rekord powstał/zniknął (`Model.objects.filter(...).exists()`)
- Dla widoków wyświetlających dane: sprawdź że kluczowy fragment treści jest w `response.content`
- Dla przekierowań: sprawdź `response.status_code == 302` ORAZ `response['Location']`
- Dla formularzy: wyślij dane przez POST i sprawdź stan bazy po przetworzeniu

**C. Minimum jeden test edge-case / guard:**
Przynajmniej jeden z poniższych (wybierz pasujący do feature'u):
- Niezalogowany użytkownik dostaje redirect na login (dla endpointów z `@login_required`)
- Duplikat nie jest tworzony po ponownym żądaniu
- Brak rekordu zwraca 404
- Nieautoryzowany użytkownik nie może modyfikować cudzych danych

**D. Falsyfikowalność** — każdy test MUSI wykryć brak implementacji:
- Nie pisz `assert response.status_code in (200, 302)` — to przechodzi nawet dla nieistniejącego endpointu (dostaje 302 redirect na login)
- Zamiast tego: sprawdź konkretną treść, konkretny rekord w bazie, konkretny URL przekierowania
- Dopuszczalne wyjątki: testy modeli (`.search()`, `__str__`) — tam weryfikuj wynik metody

**E. Styl zgodny z istniejącymi testami:**
- Używaj helpera `login_user(client, django_user_model, username, password)` do logowania
- Dekoruj `@pytest.mark.django_db` wszędzie gdzie dotykasz bazy
- Nazwy funkcji: `test_<feature_snake_case>_<scenariusz>` (np. `test_like_song_creates_library_entry`)
- Importuj modele na górze pliku jeśli ich jeszcze nie ma w importach

**F. Dane testowe** — twórz minimalny zestaw danych:
```python
autor = Autor.objects.create(pseudonim="Test Artist")
album = Album.objects.create(autor=autor, tytul="Test Album", rok_wydania=2020)
song = Utwor.objects.create(autor=autor, album=album, tytul="Test Song",
                             gatunek="pop", plik_sciezka="test.mp3")
```

### Czego NIE robić
- Nie mockuj bazy danych — testy muszą uderzać w prawdziwą bazę testową
- Nie duplikuj testów, które już istnieją dla danego feature'u
- Nie pisz testów dla feature'ów z `[ ]` (niezaimplementowanych)
- Nie testuj funkcji pomocniczych Django (np. sam mechanizm `@login_required`) — testuj zachowanie aplikacji

## Krok 4 — Weryfikacja

Po dopisaniu testów uruchom suite i upewnij się, że wszystkie przechodzą:
```
docker compose run --rm web pytest -v
```

Jeśli test nie przechodzi:
1. Sprawdź czy to błąd w teście (np. zły URL, brak danych) — popraw test
2. Jeśli feature faktycznie nie działa — **nie usuwaj testu**, zamiast tego zgłoś problem użytkownikowi i zmień status feature'u w FEATURES.md z `[x]` na `[ ]`

## Krok 5 — Raport

Po zakończeniu wyświetl raport:

```
## Raport add-tests

### Pominięte (już pokryte)
- #<nr> "<nazwa>" — pokryty przez: test_<nazwa>

### Dodane testy
- #<nr> "<nazwa>" — dodano: test_<nazwa>_<scenariusz>, test_<nazwa>_<edge>

### Problemy
- #<nr> "<nazwa>" — test nie przechodzi: <opis błędu> → status zmieniony na [ ]

### Podsumowanie
Dodano <N> testów dla <M> feature'ów. Łącznie w pliku: <X> testów.
```
