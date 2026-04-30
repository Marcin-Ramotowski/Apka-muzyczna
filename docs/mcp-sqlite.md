# MCP SQLite — konfiguracja i użycie

Serwer MCP `mcp-server-sqlite` daje Claude Code bezpośredni dostęp do bazy danych SQLite projektu. Zamiast otwierać Django shell lub pisać skrypty diagnostyczne, możesz zapytać wprost: *„Jakie gatunki muzyczne są najczęściej dodawane?"* i dostać odpowiedź w sekundę.

---

## Wymagania

- **Python 3.8+** (dostępny jako `python3`)
- **uv / uvx** — lekki menedżer pakietów Pythona; `uvx` uruchamia narzędzie bez stałej instalacji

Sprawdź, czy `uvx` jest dostępne:

```bash
uvx --version
```

Jeśli nie — zainstaluj `uv` jedną komendą:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Po instalacji `uvx` pojawi się w `~/.local/bin/`. Zrestartuj terminal lub dodaj katalog do `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## Konfiguracja

Serwer konfiguruje się przez plik `.mcp.json` w katalogu projektu. Jego zawartość powinna wyglądać tak:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "/home/<twój-user>/.local/bin/uvx",
      "args": ["mcp-server-sqlite", "--db-path", "/ścieżka/do/projektu/db.sqlite3"]
    }
  }
}
```

### Konfiguracja na nowej maszynie

1. Zainstaluj `uv` (patrz wyżej).
2. Skopiuj `.mcp.json.example` do `.mcp.json` i podmień ścieżki:

```bash
cp .mcp.json.example .mcp.json
```

Następnie edytuj `.mcp.json` — zamień `<twój-user>` i ścieżkę do projektu na właściwe wartości.

> `.mcp.json` jest w `.gitignore`, bo zawiera absolutne ścieżki zależne od systemu. Każdy developer konfiguruje go lokalnie.

### Pierwsze uruchomienie

Przy pierwszym użyciu Claude Code wyświetli prompt z pytaniem o zatwierdzenie serwera — kliknij **Allow**. Serwer startuje automatycznie przy starcie sesji.

---

## Schemat bazy danych

Tabele aplikacji (bez tabel systemowych Django):

| Tabela | Model Django | Opis |
|---|---|---|
| `autor` | `Autor` | Artyści i zespoły |
| `album` | `Album` | Albumy powiązane z autorem |
| `utwor` | `Utwor` | Piosenki (MP3, gatunek, tekst) |
| `uzytkownik` | `Uzytkownik` | Użytkownicy (rozszerza `AbstractUser`) |
| `playlista` | `Playlista` | Playlisty użytkowników |
| `playlista_utwor` | `BibliotekaPlaylist` | Piosenki w playliście (M2M) |
| `subskrypcja` | `Subskrypcja` | Subskrypcje artystów (M2M) |
| `biblioteka_piosenki` | `BibliotekaPiosenek` | Polubione piosenki (M2M) |
| `biblioteka_albumy` | `BibliotekaAlbumow` | Polubione albumy (M2M) |
| `biblioteka_playlisty` | `PlaylistyUzytkownika` | Zapisane playlisty (M2M) |
| `listening_history` | `ListeningHistory` | Historia odtworzeń z timestampem |

---

## Przykłady użycia

Poniżej przykłady zapytań, które możesz zadać Claude Code wprost w rozmowie po skonfigurowaniu serwera.

### Przegląd danych

```
Ile mamy autorów, albumów i piosenek w bazie?
```

```
Pokaż wszystkich autorów z liczbą ich albumów, posortowanych malejąco.
```

```
Jakie gatunki muzyczne występują w bazie i ile piosenek ma każdy?
```

### Aktywność użytkowników

```
Którzy użytkownicy mają najwięcej polubionych piosenek?
```

```
Pokaż historię odtworzeń z ostatnich 7 dni — ile sesji dziennie?
```

```
Którzy użytkownicy są premium, a którzy free?
```

### Debugowanie

```
Czy są piosenki bez przypisanego pliku MP3 (plik_sciezka = '')?
```

```
Znajdź duplikaty — piosenki tego samego autora z identycznym tytułem.
```

```
Czy są albumy bez żadnych piosenek?
```

### Rekomendacje i biblioteki

```
Jakie gatunki są najczęściej polubiane przez użytkowników?
```

```
Pokaż piosenki, które są na co najmniej 3 różnych playlistach.
```

```
Którzy autorzy mają subskrybentów, ale żadna ich piosenka nie jest polubiona?
```

---

## Ograniczenia

- Serwer działa na **bazie developerskiej** (`db.sqlite3`). Nie ma dostępu do bazy testowej — ta jest tworzona in-memory przez pytest i żyje tylko przez czas testu.
- Serwer ma dostęp **tylko do odczytu** — nie wykona `INSERT`, `UPDATE` ani `DELETE`. Modyfikacje danych zawsze przez Django ORM lub `manage.py shell`.
- Baza jest aktualna do ostatniego `docker compose up` — migracje niezastosowane lokalnie nie będą widoczne w schemacie.

---

## Rozwiązywanie problemów

**Serwer nie startuje / brak narzędzi `mcp__sqlite__*`**

Sprawdź, czy ścieżka do `uvx` w `.mcp.json` jest poprawna:
```bash
which uvx
```
Zaktualizuj pole `command` w `.mcp.json` do wyniku tej komendy.

**`db.sqlite3` nie istnieje**

Uruchom migracje lokalnie:
```bash
python manage.py migrate
# lub przez Docker:
docker compose up
```

**Serwer jest dostępny, ale zapytania zwracają puste wyniki**

Baza developerska może być pusta. Dodaj dane przez panel admina (`/admin/`) lub załaduj fixture:
```bash
python manage.py loaddata nazwa_fixture.json
```
