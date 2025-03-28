# Generated by Django 5.1.1 on 2025-03-04 10:51

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Wallet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "balance",
                    models.BigIntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, message="Balance cannot be negative."
                            )
                        ],
                    ),
                ),
                (
                    "frozen_amount",
                    models.BigIntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, message="Frozen amount cannot be negative."
                            )
                        ],
                    ),
                ),
                ("is_restricted", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wallet_owner",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("credit", "Credit"), ("debit", "Debit")],
                        max_length=10,
                    ),
                ),
                (
                    "amount",
                    models.BigIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, message="Amount must be at least 1."
                            )
                        ]
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="wallets.wallet",
                    ),
                ),
            ],
        ),
    ]
