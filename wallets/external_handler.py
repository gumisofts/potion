import os

import requests


def send_money_external(acc, bank, amount, remarks):
    """
    Send money to an external wallet using a third-party API.

    :param wallet_id: The ID of the external wallet.
    :param amount: The amount to send.
    :param remarks: Additional remarks for the transaction.
    :return: Response from the external API.
    """

    url = "https://myme-742i.vercel.app/banks/receive/external/"
    headers = {
        "X-Access-Id": os.getenv("EXTERNAL_ACCESS_ID"),
        "X-Access-Secret": os.getenv("EXTERNAL_ACCESS_SECRET"),
        "Content-Type": "application/json",
    }

    payload = {
        "destination_account": acc,
        "receiver_bank": bank,
        "amount": amount,
        "remarks": remarks,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()  # Raise an error for bad responses
