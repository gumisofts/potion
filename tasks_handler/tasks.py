from datetime import datetime, timedelta

from celery import group, shared_task
from django.db import transaction
from django.utils import timezone

from subscriptions.models import Subscription, UserSubscription
from wallets.models import Transaction


@shared_task
def dispatch_subscription_payment():
    subscriptions = UserSubscription.objects.filter(
        is_active=True, next_billing_date=timezone.now()
    )

    for subscription in subscriptions:
        handle_one_subscription(subscription).delay()


@shared_task
def handle_one_subscription(user_subscription):

    with transaction.atomic():

        user = user_subscription.user
        from_wallet = user.wallet
        to_be_deducted_amount = user_subscription.subscription.fixed_price
        to_wallet = user_subscription.subscription.bussines.wallet

        tr = Transaction.objects.create(
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=to_be_deducted_amount,
            remarks=f"Payment for subscription on {user_subscription.subscription.name}",
            status="pending",
        )

        user_subscription.next_billing_date = timezone.now() + timedelta(
            days=user_subscription.subscription.frequency
        )
        user_subscription.save()
