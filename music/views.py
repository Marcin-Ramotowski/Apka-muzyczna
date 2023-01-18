from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.views.generic import FormView
from .models import Autor, Utwor, Album, Playlista
from .forms import SearchForm


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
        for field in results:
            print(field)
        return render(request, self.template_name, {'form': form, 'results': results})
