from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.views.generic import FormView
from .forms import SearchForm, RegisterForm
from .models import Autor, Utwor, Album, Playlista


def start(request):
    return render(request, 'start.html')


@login_required
def profile(request):
    return render(request, 'profile.html', {'username': request.user})


class BaseLoginView(LoginView):
    template_name = 'login.html'


class BaseLogoutView(LogoutView):
    template_name = 'start.html'


class SearchFormView(FormView):
    template_name = 'search.html'
    form_class = SearchForm

    def post(self, request, *args, **kwargs):
        models = {'autor': Autor, 'piosenka': Utwor, 'album': Album, 'playlista': Playlista}
        filter_fields = {'autor': ('imie', 'nazwisko'), 'piosenka': ('tytul', 'gatunek'),
                         'album': ('tytul', 'rok_wydania'), 'playlista': ('nazwa',)}
        form = self.form_class(request.POST)
        query = form.data['query']
        database_sign = form.data['database']
        database = models[database_sign]
        fields = filter_fields[database_sign]
        results = database.objects.filter(**{fields[0]: query})
        results = results.values_list(*fields)
        return render(request, self.template_name, {'form': form, 'results': results})


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Rejestracja zakończona pomyślnie')
            return redirect('music:profile')
        messages.error(request, 'Nieudana rejestracja. Nieprawidłowe informacje.')
        return render(request, 'register.html', {'form': form})
