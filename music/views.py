from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView
from django.http import StreamingHttpResponse
from .forms import SearchForm, RegisterForm, UploadForm
from .models import *
import mimetypes


def start(request):
    return render(request, 'start.html')


@login_required(login_url='/login')
def profile(request):
    username = request.user
    user_id = request.user.id

    songs_ids = BibliotekaPiosenek.objects.filter(uzytkownik_id=user_id)
    songs = [get_object_or_404(Utwor, utwor_id=record.utwor_id) for record in songs_ids]

    authors_ids = Subskrypcja.objects.filter(uzytkownik_id=user_id)
    authors = [get_object_or_404(Autor, autor_id=record.autor_id) for record in authors_ids]

    albums_ids = BibliotekaAlbumow.objects.filter(uzytkownik_id=user_id)
    albums = [get_object_or_404(Album, album_id=record.album_id) for record in albums_ids]

    # playlists_ids = BibliotekaPlaylist.objects.filter(uzytkownik_id=user_id)
    # playlists = [get_object_or_404(Playlista, playlista_id=record.playlista_id) for record in playlists_ids]
    return render(request, 'profile.html', {'username': username, 'songs': songs, 'authors': authors,
                                            'albums': albums, 'playlists': ()})


@login_required(login_url='/login')
def download_file(request, filename):
    fl_path = 'music/static/media/' + filename
    fl = open(fl_path, 'rb')
    mime_type = mimetypes.guess_type(fl_path)[0]
    response = StreamingHttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = f"attachment; filename={filename}"
    return response


class UploadView(FormView, LoginRequiredMixin):
    template_name = 'upload.html'
    form_class = UploadForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            path = f'C:\\Users\\asus\\Python Projekty\\Apka_muzyczna\\music\\static\\media\\' \
                   f'{form.data["title"]}.mp3'
            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            messages.success(request, 'Pomyślnie załadowano plik.')
            return redirect('music:profile')
        else:
            form = UploadForm()
            return render(request, self.template_name, context={'errors': form.errors, 'form': form})


class BaseLoginView(LoginView):
    template_name = 'login.html'


class BaseLogoutView(LogoutView, LoginRequiredMixin):
    template_name = 'start.html'


class SearchFormView(FormView, LoginRequiredMixin):
    template_name = 'search.html'
    form_class = SearchForm

    def post(self, request, *args, **kwargs):
        models = {'autor': Autor, 'piosenka': Utwor, 'album': Album, 'playlista': Playlista}
        filter_fields = {'autor': 'imie__contains', 'piosenka': 'tytul__contains',
                         'album': 'tytul__contains', 'playlista': 'nazwa__contains'}
        form = self.form_class(request.POST)
        query = form.data['query']
        database_sign = form.data['database']  # pobieramy wybraną przez użytkownika tabelę
        database = models[database_sign]  # pobieramy klasę reprezentującą wybraną tabelę
        field = filter_fields[database_sign]  # wybieramy pole, po którym filtrujemy
        results = database.objects.filter(**{field: query})  # filtrujemy po wybranym polu dopasowując do query
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
