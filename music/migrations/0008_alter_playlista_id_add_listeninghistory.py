from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0007_rename_tekst_utwor_tekst_sciezka'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlista',
            name='playlista_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='ListeningHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('played_at', models.DateTimeField(auto_now_add=True)),
                ('utwor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='play_history',
                    to='music.utwor',
                )),
                ('uzytkownik', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='listening_history',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'listening_history',
                'ordering': ['-played_at'],
            },
        ),
    ]
