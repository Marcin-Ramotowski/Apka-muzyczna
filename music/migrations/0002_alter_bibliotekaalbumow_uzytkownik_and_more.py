# Generated by Django 4.1.5 on 2023-02-03 20:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bibliotekaalbumow',
            name='uzytkownik',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_albums_library', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bibliotekapiosenek',
            name='uzytkownik',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_songs_library', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='PlaylistyUzytkownika',
            fields=[
                ('library_playlist_id', models.IntegerField(primary_key=True, serialize=False)),
                ('playlista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playlists_in_library', to='music.playlista')),
                ('uzytkownik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_playlists_library', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'biblioteka_playlisty',
            },
        ),
    ]
