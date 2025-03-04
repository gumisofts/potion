# Generated by Django 5.1.1 on 2025-03-04 10:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('wallets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='wallet',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_wallet', to='wallets.wallet'),
        ),
        migrations.AddField(
            model_name='business',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='businesses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='business',
            name='wallet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_wallets', to='wallets.wallet'),
        ),
        migrations.AddField(
            model_name='service',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='accounts.business'),
        ),
    ]
