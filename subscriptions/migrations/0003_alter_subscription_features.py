# Generated by Django 5.1.1 on 2025-05-07 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0002_subscriptionfeature_subscription_features"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="features",
            field=models.ManyToManyField(
                blank=True,
                related_name="features",
                to="subscriptions.subscriptionfeature",
            ),
        ),
    ]
