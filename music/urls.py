from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.start, name='start'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.SearchFormView.as_view(), name='search'),
    path('download/<str:filename>', views.download_file, name='download'),
    path('upload/', views.UploadView.as_view(), name='upload'),
    path('like/<str:model_name>/<int:record_id>', views.like, name='like'),
    path('unlike/<str:model_name>/<int:record_id>', views.unlike, name='unlike'),
    path('play/<str:filename>', views.play, name='play'),
    path('songs/<str:model_name>/<int:record_id>', views.display_songs, name='songs'),
    path('text/<int:record_id>', views.display_text, name='text'),
    path('history/', views.history, name='history'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/add-song/', views.add_song_to_playlist, name='add_song_to_playlist'),
    path('text/upload/<int:record_id>', views.upload_text, name='upload_text'),
    path('play-random-liked/', views.play_random_liked, name='play_random_liked'),
    path('history/record/<int:song_id>/', views.record_play, name='record_play'),
]
