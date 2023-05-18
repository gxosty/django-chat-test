# Generated by Django 4.2.1 on 2023-05-18 15:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_active', models.DateTimeField()),
                ('relationship', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.relationship')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_date', models.DateTimeField()),
                ('text', models.TextField()),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.privatechat')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]