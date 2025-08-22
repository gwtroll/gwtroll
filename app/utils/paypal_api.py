import requests
import os
from datetime import datetime, timedelta
import json

PAYPAL_API_BASE_URL = "https://api-m.sandbox.paypal.com"
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.environ.get("PAYPAL_SECRET")

access_token = None
access_token_cache = datetime.now()


class PayPal_Invoice:
    def __init__(self, registrations, invoice_email):
        self.detail = {
            "currency_code": "USD",
            "invoice_number": str(get_invoice_number()),
            "invoice_data": datetime.now().date().strftime("%m/%d/%Y"),
            "note": "TEST NOTE",
            "term": "NET 7",
            "memo": "TEST MEMO",
        }
        self.invoicer = {
            "name": {"given_name": "SCA-Gulf Wars", "surname": "Inc"},
            # 'email_address':'gwincpp@gmail.com',
            "email_address": "sb-6x1ar45446347@business.example.com",
            "website": "www.gulfwars.org",
        }
        self.primary_recipients = [{"billing_info": {"email_address": invoice_email}}]
        items = []
        for reg in registrations:
            items.extend(reg.get_invoice_items())
        self.items = items


def get_accesstoken():
    global access_token
    global access_token_cache
    if access_token is not None and access_token_cache > datetime.now():
        return access_token
    else:
        url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials"}
        response = requests.post(
            url, headers=headers, data=data, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
        )

        if response.status_code == 200:
            data_dict = response.json()
            access_token_cache = datetime.now() + timedelta(
                seconds=int(data_dict["expires_in"]) - 100
            )
            access_token = "Bearer " + data_dict["access_token"]
            return access_token


def create_invoice(registrations, invoice_email):
    url = "https://api-m.sandbox.paypal.com/v2/invoicing/invoices"

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    new_invoice = PayPal_Invoice(registrations, invoice_email)

    data = json.dumps(new_invoice.__dict__)

    response = requests.post(url, headers=headers, data=data)

    data_dict = response.json()

    return data_dict


def send_invoice(invoice_id):
    url = f"https://api-m.sandbox.paypal.com/v2/invoicing/invoices/{invoice_id}/send"

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
    }

    data = '{ "send_to_invoicer": true }'

    response = requests.post(url, headers=headers, data=data)
    print(response.json())


def get_invoice_number():
    url = "https://api-m.sandbox.paypal.com/v2/invoicing/generate-next-invoice-number"

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
    }
    data = "{}"

    response = requests.post(url, headers=headers, data=data)

    data_dict = response.json()

    print(data_dict)

    return data_dict["invoice_number"]


def verify_webhook_signature(auth_algo, cert_url, transmission_id, transmission_sig, transmission_time, webhook_event):

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
    }

    data = {
        "auth_algo": auth_algo,
        "cert_url": cert_url,
        "transmission_id": transmission_id,
        "transmission_sig": transmission_sig,
        "transmission_time": transmission_time,
        "webhook_id": "53K43429G57369229",
        "webhook_event": webhook_event,
    }

    response = requests.post(
        "https://api-m.sandbox.paypal.com/v1/notifications/verify-webhook-signature",
        headers=headers,
        data=json.dumps(data),
    )

    data_dict = response.json()

    print(data_dict)

    if data_dict['verification_status'] == "SUCCESS":
        return True
    else:
        return False
