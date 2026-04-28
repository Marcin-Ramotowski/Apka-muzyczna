from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView
from django.http import StreamingHttpResponse, FileResponse, Http404
from Apka_muzyczna.settings import BASE_DIR, MEDIA_URL
from .forms import SearchForm, RegisterForm, UploadForm, HistoryFilterForm, PlaylistForm, AddSongToPlaylistForm
from .models import (
    Autor, Album, Utwor, Uzytkownik, Playlista, Subskrypcja,
    BibliotekaPiosenek, PlaylistyUzytkownika, BibliotekaAlbumow,
    BibliotekaPlaylist, ListeningHistory,
)
import os


def start(request):
    return render(request, 'start.html')


@login_required(login_url='/login')
def profile(request):
    username = request.user
    user_id = request.user.id
    user = get_object_or_404(Uzytkownik, id=user_id)

    songs = user.user_songs_library.all()
    authors = user.subscriptions_user.all()
    albums = user.user_albums_library.all()
    playlists = user.user_playlists_library.all()

    return render(request, 'profile.html', {'username': username, 'songs': songs, 'authors': authors,
                                            'albums': albums, 'playlists': playlists})


@login_required(login_url='/login')
def display_text(request, record_id):
    song = get_object_or_404(Utwor, utwor_id=record_id)
    path = 'music/static/tekst/' + song.tekst_sciezka
    with open(path, 'r', encoding='utf-8') as file:
        text = file.readlines()
    return render(request, 'song_text.html', {'song': song, 'text': text})


@login_required(login_url='/login')
def download_file(request, filename):
    fl_path = MEDIA_URL + filename
    fl = open(fl_path, 'rb')
    response = StreamingHttpResponse(fl, content_type='audio/mpeg')
    response['Content-Disposition'] = f"attachment; filename={filename}"
    response['Content-Length'] = os.path.getsize(fl_path)
    return response


@login_required(login_url='/login')
def like(request, model_name, record_id):
    models = {'autor': Subskrypcja, 'utwor': BibliotekaPiosenek, 'album': BibliotekaAlbumow,
              'playlista': PlaylistyUzytkownika}
    user_id = request.user.id
    model = models[model_name]
    second_field = model_name + '_id'

    record = model.objects.filter(**{'uzytkownik_id': user_id, f'{second_field}': record_id}).first()
    if record:
        messages.info(request, 'Już polubiłeś.')
    else:
        model.objects.create(**{'uzytkownik_id': user_id, f'{second_field}': record_id})
        messages.success(request, 'Polubiono pomyślnie')
    return redirect('music:search')


@login_required(login_url='/login')
def unlike(request, model_name, record_id):
    models = {'autor': Subskrypcja, 'utwor': BibliotekaPiosenek, 'album': BibliotekaAlbumow,
              'playlista': PlaylistyUzytkownika}
    model = models[model_name]
    record = get_object_or_404(model, id=record_id)
    record.delete()
    return redirect('music:profile')


@login_required(login_url='/login')
def play(request, filename):
    file_path = MEDIA_URL + filename
    file = open(file_path, 'rb')
    response = FileResponse(file, content_type='audio/mpeg')
    response['Content-Length'] = os.path.getsize(file_path)

    song = Utwor.objects.filter(plik_sciezka=filename).first()
    if song:
        ListeningHistory.objects.create(uzytkownik=request.user, utwor=song)

    return response


@login_required(login_url='/login')
def display_songs(request, model_name, record_id):
    if model_name == 'album':
        collection = get_object_or_404(Album, album_id=record_id)
        songs = collection.songs_in_album.all()
        header = 'Album '
    elif model_name == 'playlista':
        collection = get_object_or_404(Playlista, playlista_id=record_id)
        songs = collection.songs_in_playlist.all()
        header = 'Playlista '
    else:
        raise Http404('Podany typ obiektu nie jest zbiorem piosenek.')
    return render(request, 'list_songs.html', {'header': header, 'collection': collection, 'songs': songs})


@login_required(login_url='/login')
def history(request):
    form = HistoryFilterForm(request.GET or None)
    entries = request.user.listening_history.select_related('utwor', 'utwor__autor')

    if form.is_valid():
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        if date_from:
            entries = entries.filter(played_at__date__gte=date_from)
        if date_to:
            entries = entries.filter(played_at__date__lte=date_to)

    return render(request, 'history.html', {'form': form, 'entries': entries})


@login_required(login_url='/login')
def recommendations(request):
    user = request.user
    liked_genres = (
        BibliotekaPiosenek.objects
        .filter(uzytkownik=user)
        .values_list('utwor__gatunek', flat=True)
    )
    subscribed_author_ids = (
        Subskrypcja.objects
        .filter(uzytkownik=user)
        .values_list('autor_id', flat=True)
    )
    already_liked_ids = (
        BibliotekaPiosenek.objects
        .filter(uzytkownik=user)
        .values_list('utwor_id', flat=True)
    )

    recommended = (
        Utwor.objects
        .filter(Q(gatunek__in=liked_genres) | Q(autor_id__in=subscribed_author_ids))
        .exclude(utwor_id__in=already_liked_ids)
        .select_related('autor', 'album')
        .distinct()[:20]
    )

    return render(request, 'recommendations.html', {'songs': recommended})


@login_required(login_url='/login')
def create_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            try:
                form.validate_unique_for_user(request.user)
            except Exception as e:
                messages.error(request, str(e))
                return render(request, 'create_playlist.html', {'form': form})

            playlist = Playlista.objects.create(
                uzytkownik=request.user,
                nazwa=form.cleaned_data['name'],
            )
            PlaylistyUzytkownika.objects.create(
                uzytkownik=request.user,
                playlista=playlist,
            )
            messages.success(request, f'Playlista „{playlist.nazwa}" została utworzona.')
            return redirect('music:profile')
    else:
        form = PlaylistForm()
    return render(request, 'create_playlist.html', {'form': form})


@login_required(login_url='/login')
def add_song_to_playlist(request):
    user = request.user

    if request.method == 'POST':
        form = AddSongToPlaylistForm(request.POST)
        if form.is_valid():
            playlist_id = form.cleaned_data['playlist_id']
            song_id = form.cleaned_data['song_id']

            playlist = get_object_or_404(Playlista, pk=playlist_id)
            if playlist.uzytkownik != user:
                messages.error(request, 'Nie masz uprawnień do tej playlisty.')
                return redirect('music:profile')

            song = get_object_or_404(Utwor, pk=song_id)
            already_in = BibliotekaPlaylist.objects.filter(playlista=playlist, utwor=song).exists()
            if already_in:
                messages.info(request, 'Utwór już znajduje się na tej playliście.')
            else:
                BibliotekaPlaylist.objects.create(playlista=playlist, utwor=song)
                messages.success(request, f'Dodano „{song.tytul}" do playlisty „{playlist.nazwa}".')
            return redirect('music:profile')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text()[2:])

    user_playlists = Playlista.objects.filter(uzytkownik=user)
    all_songs = Utwor.objects.select_related('autor').all()
    form = AddSongToPlaylistForm()
    return render(request, 'add_song_to_playlist.html', {
        'form': form,
        'user_playlists': user_playlists,
        'all_songs': all_songs,
    })


class UploadView(LoginRequiredMixin, FormView):
    login_url = '/login'
    template_name = 'upload.html'
    form_class = UploadForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            song_title = cd['title']
            genre = cd['genre']
            autor_data = cd['autor']
            name = autor_data.get('name')
            surname = autor_data.get('surname')
            nick = autor_data.get('nick')
            album_data = cd['album']
            album_title = album_data.get('title')
            year_publishing = album_data.get('published_year')

            autor = Autor.objects.filter(imie=name, nazwisko=surname).first()
            if not autor:
                autor = Autor.objects.create(imie=name, nazwisko=surname, pseudonim=nick)
            album = Album.objects.filter(tytul=album_title, rok_wydania=year_publishing).first()
            if not album:
                album = Album.objects.create(autor_id=autor.autor_id, tytul=album_title, rok_wydania=year_publishing)

            artist = autor.pseudonim if autor.pseudonim else f'{autor.imie} {autor.nazwisko}'
            file_path = f'{artist} - {cd["title"]}.mp3'
            file = request.FILES['file']

            utwor = Utwor.objects.filter(autor_id=autor.autor_id, tytul=song_title).first()
            if utwor:
                messages.info(request, 'Ten utwór już znajduje się w bazie.')
                return redirect('music:upload')
            else:
                Utwor.objects.create(autor_id=autor.autor_id, album_id=album.album_id, tytul=song_title,
                                     gatunek=genre, plik_sciezka=file_path)
                messages.success(request, 'Pomyślnie zapisano utwór w bazie.')

            absolute_path = BASE_DIR / MEDIA_URL / file_path
            with open(absolute_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            messages.success(request, 'Pomyślnie załadowano plik.')
            return redirect('music:profile')
        else:
            for error in form.errors.values():
                text = error.as_text()[2:]
                messages.error(request, text)
            form = self.form_class()
            return render(request, self.template_name, context={'form': form})


class BaseLoginView(LoginView):
    template_name = 'login.html'


class BaseLogoutView(LogoutView):
    template_name = 'start.html'


class SearchFormView(LoginRequiredMixin, FormView):
    login_url = '/login'
    template_name = 'search.html'
    form_class = SearchForm

    def post(self, request, *args, **kwargs):
        models = {'autor': Autor, 'piosenka': Utwor, 'album': Album, 'playlista': Playlista}
        form = self.form_class(request.POST)
        query = form.data['query']
        database_sign = form.data['database']  # pobieramy wybraną przez użytkownika tabelę
        model = models[database_sign]  # pobieramy klasę reprezentującą wybraną tabelę
        results = model.search(query)
        return render(request, self.template_name, {'form': form, 'results': results, 'model': database_sign})


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Rejestracja zakończona pomyślnie.')
            return redirect('music:profile')
        messages.error(request, 'Nieudana rejestracja. Nieprawidłowe informacje.')
        return render(request, 'register.html', {'form': form})
