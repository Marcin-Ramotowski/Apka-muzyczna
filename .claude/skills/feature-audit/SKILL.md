---
name: feature-audit
description: Use this skill to verify that FEATURES.md reflects the actual state of the codebase. Triggers include phrases like "zaktualizuj FEATURES.md", "sprawdź features", "czy features są aktualne", "zweryfikuj implementację", "audit features", "sync features", "check what's implemented". Compares every [x] and [ ] entry against views.py and urls.py, fixes mismatches, and adds missing entries.
---

Przeprowadź audyt pliku `FEATURES.md` dla projektu **Apka-muzyczna** — sprawdź, czy każda funkcja oznaczona `[x]` jest faktycznie zaimplementowana w kodzie. Następnie zaktualizuj plik tak, by odzwierciedlał rzeczywisty stan.

## Instrukcja

### Krok 1 — Zbierz bazę wiedzy
Przeczytaj kolejno (nie pomijaj żadnego):
- `FEATURES.md` — lista funkcji z oznaczeniami `[x]` / `[ ]`
- `music/views.py` — pełna zawartość
- `music/urls.py` — pełna zawartość
- `music/models.py` — pełna zawartość
- `music/forms.py` — pełna zawartość

### Krok 2 — Weryfikacja każdej funkcji oznaczonej `[x]`
Dla każdego wiersza z `[x]` w FEATURES.md sprawdź:

1. **Endpoint istnieje** — czy URL z kolumny "Endpoint" jest zarejestrowany w `urls.py`?
2. **Widok istnieje** — czy odpowiedni widok/funkcja jest zdefiniowana w `views.py`?
3. **Model obsługuje feature** — czy model wymieniony w opisie istnieje i ma potrzebne pola?
4. **Formularz istnieje** — jeśli feature wymaga formularza, czy jest w `forms.py`?

Dla funkcji oznaczonych `[ ]` sprawdź odwrotnie: może są już zaimplementowane, a oznaczenie nie zostało zaktualizowane.

### Krok 3 — Zidentyfikuj rozbieżności
Sporządź wewnętrzną listę rozbieżności w jednej z kategorii:
- **Fałszywe `[x]`** — feature oznaczony jako gotowy, ale brak implementacji w kodzie
- **Fałszywe `[ ]`** — feature oznaczony jako niezaimplementowany, ale kod już istnieje
- **Brakujące wpisy** — w kodzie istnieje widok/URL, którego w ogóle nie ma w FEATURES.md

### Krok 4 — Zaktualizuj `FEATURES.md`
Wprowadź zmiany bezpośrednio w pliku:
- Zmień `[x]` → `[ ]` dla funkcji bez implementacji
- Zmień `[ ]` → `[x]` dla funkcji, które są już zaimplementowane
- Dopisz brakujące wiersze dla widoków/URLi obecnych w kodzie, ale nieobecnych w pliku — przypisz kolejny wolny numer
- Zachowaj dokładnie obecny format Markdown (tabele, nagłówki sekcji, kolumny)

### Krok 5 — Raport
Po zaktualizowaniu pliku wyświetl zwięzły raport w formacie:

```
## Raport audytu FEATURES.md

### Zmienione oznaczenia
- #<nr> "<nazwa>" — [x] → [ ] (brak widoku/URLa w kodzie)
- #<nr> "<nazwa>" — [ ] → [x] (znaleziono implementację: views.<funkcja>)

### Nowe wpisy
- #<nr> "<nazwa>" — dodano (endpoint: <url>)

### Bez zmian
- Liczba funkcji bez zmian: <N>

### Podsumowanie
FEATURES.md zaktualizowany: <data>. Łącznie: <N> zaimplementowanych / <M> zaplanowanych.
```

Jeśli nie ma żadnych rozbieżności, napisz "FEATURES.md jest aktualny — brak rozbieżności." i nie modyfikuj pliku.
