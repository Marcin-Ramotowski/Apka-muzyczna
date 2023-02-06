from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView
from django.http import StreamingHttpResponse, FileResponse
from .forms import SearchForm, RegisterForm, UploadForm
from .models import Autor, Album, Utwor, Uzytkownik, Playlista, Subskrypcja, \
    BibliotekaPiosenek, PlaylistyUzytkownika, BibliotekaAlbumow
import mimetypes
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
def download_file(request, filename):
    fl_path = 'music/static/media/' + filename
    fl = open(fl_path, 'rb')
    mime_type = mimetypes.guess_type(fl_path)[0]
    response = StreamingHttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = f"attachment; filename={filename}"
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
    file_path = 'music/static/media/' + filename
    file = open(file_path, 'rb')
    response = FileResponse(file, content_type='audio/mpeg')
    response['Content-Length'] = os.path.getsize(file_path)
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
