# Generated by Django 5.1.1 on 2025-03-19 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "subscriptions",
            "0002_remove_usersubscription_unique_user_subscription_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="usersubscription",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
