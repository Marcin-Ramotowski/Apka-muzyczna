from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView
from django.http import StreamingHttpResponse, FileResponse, Http404
from Apka_muzyczna.settings import BASE_DIR, MEDIA_URL
from .forms import SearchForm, RegisterForm, UploadForm
from .models import Autor, Album, Utwor, Uzytkownik, Playlista, Subskrypcja, \
    BibliotekaPiosenek, PlaylistyUzytkownika, BibliotekaAlbumow
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
