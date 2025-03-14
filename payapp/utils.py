import requests
from decimal import Decimal
from django.conf import settings

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount, to_currency

    response = requests.post(
        f"{settings.SITE_URL}/api/convert/",
        json={
            "amount": str(amount),
            "from_currency": from_currency,
            "to_currency": to_currency
        },
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        data = response.json()
        return Decimal(data['converted_amount']), data['currency']
    raise ValueError("Currency conversion failed")