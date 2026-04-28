# Feature Catalog — Apka-muzyczna

Status legend: `[x]` implemented · `[ ]` planned / not yet implemented

---

## Authentication & Accounts

| # | Feature | Status | Endpoint |
|---|---------|--------|----------|
| 1 | User registration (first name, last name, username, email, password) | `[x]` | `POST /register/` |
| 2 | Login | `[x]` | `POST /login/` |
| 3 | Logout | `[x]` | `POST /logout/` |
| 4 | Account types: free / premium | `[x]` | — (model field) |
| 5 | Password reset | `[ ]` | — |

---

## User Profile & Library

| # | Feature | Status | Endpoint |
|---|---------|--------|----------|
| 6 | Profile page — shows liked songs, subscribed authors, liked albums, saved playlists | `[x]` | `GET /profile/` |
| 7 | Add song to library (like) | `[x]` | `GET /like/utwor/<id>` |
| 8 | Add album to library (like) | `[x]` | `GET /like/album/<id>` |
| 9 | Subscribe to author | `[x]` | `GET /like/autor/<id>` |
| 10 | Save playlist to library | `[x]` | `GET /like/playlista/<id>` |
| 11 | Remove song from library (unlike) | `[x]` | `GET /unlike/utwor/<id>` |
| 12 | Remove album from library | `[x]` | `GET /unlike/album/<id>` |
| 13 | Unsubscribe from author | `[x]` | `GET /unlike/autor/<id>` |
| 14 | Remove playlist from library | `[x]` | `GET /unlike/playlista/<id>` |
| 15 | Duplicate-like guard (info message instead of error) | `[x]` | — |

---

## Search

| # | Feature | Status | Endpoint |
|---|---------|--------|----------|
| 16 | Search by author (name, surname, nick) | `[x]` | `POST /search/` |
| 17 | Search by song (title, genre, author) | `[x]` | `POST /search/` |
| 18 | Search by album (title, author; numeric query matches release year) | `[x]` | `POST /search/` |
| 19 | Search by playlist (name) | `[x]` | `POST /search/` |

---

## Playback & Content

| # | Feature | Status | Endpoint |
|---|---------|--------|----------|
| 20 | Stream MP3 in browser | `[x]` | `GET /play/<filename>` |
| 21 | Download MP3 file | `[x]` | `GET /download/<filename>` |
| 22 | Display song lyrics | `[x]` | `GET /text/<id>` |
| 23 | List songs in an album | `[x]` | `GET /songs/album/<id>` |
| 24 | List songs in a playlist | `[x]` | `GET /songs/playlista/<id>` |

---

## Upload

| # | Feature | Status | Endpoint |
|---|---------|--------|----------|
| 25 | Upload MP3 with metadata (title, genre, author, album) | `[x]` | `POST /upload/` |
| 26 | Auto-create author record if not found | `[x]` | — |
| 27 | Auto-create album record if not found | `[x]` | — |
| 28 | Duplicate song guard (blocks re-upload of same author + title) | `[x]` | — |
| 29 | Upload song lyrics | `[ ]` | — |

---

## Data Models

| Model | Description |
|-------|-------------|
| `Autor` | Artist or band (name, surname, nick, type, bio) |
| `Album` | Album linked to an author (title, release year, bio) |
| `Utwor` | Song linked to author + album (title, genre, MP3 path, lyrics path) |
| `Uzytkownik` | Custom user model extending `AbstractUser` (free/premium) |
| `Playlista` | Playlist owned by a user |
| `BibliotekaPlaylist` | M2M: songs within a playlist |
| `Subskrypcja` | M2M: user ↔ author subscriptions |
| `BibliotekaPiosenek` | M2M: user ↔ liked songs |
| `BibliotekaAlbumow` | M2M: user ↔ liked albums |
| `PlaylistyUzytkownika` | M2M: user ↔ saved playlists |

---

## Administration & Infrastructure

| # | Feature | Status |
|---|---------|--------|
| 30 | Django admin panel | `[x]` |
| 31 | Docker + docker-compose setup | `[x]` |
| 32 | Auto-run migrations on container start | `[x]` |
| 33 | CI pipeline (Jenkinsfile) | `[x]` |
| 34 | pytest test suite | `[x]` |
