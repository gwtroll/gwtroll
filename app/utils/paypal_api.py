import requests
import os
from datetime import datetime, timedelta
import json
import pytz
from app.models import EventVariables

PAYPAL_API_BASE_URL = os.environ.get('PAYPAL_API_BASE_URL')
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.environ.get("PAYPAL_SECRET")
PAYPAL_PAYMENT_WEBHOOK_ID = os.environ.get("PAYPAL_PAYMENT_WEBHOOK_ID")

access_token = None
access_token_cache = datetime.now()


class PayPal_Invoice:
    def __init__(self, registrations, invoice_email, type):
        if type == 'REGISTRATION':
            self.detail = {
                "reference": "Gulf Wars XXXIV (2026)",
                "currency_code": "USD",
                "invoice_number": str(get_invoice_number()),
                "invoice_date": datetime.now(pytz.timezone('America/Chicago')).strftime("%Y-%m-%d"),
                "note": "Gulf Wars XXXIV- A war with no enemies! "
                "\nALL INVOICES MUST BE PAID WITHIN 7 DAYS OR THE RESERVATION MAY BE CANCELLED."
                "\nRegistrations will be closed February 21, 2026 with payment due by February 28, 2026.",
                "payment_term": {
                    "term_type": "DUE_ON_DATE_SPECIFIED",
                    "due_date": (datetime.now(pytz.timezone('America/Chicago')) + timedelta(days=7)).strftime("%Y-%m-%d")
                    },
                "memo": "Pre-Registration",
                "terms_and_conditions": "Terms and Conditions (Registrations)"
                "\n1. Please pay invoice by the due date or your reservation may be cancelled."
                "\n2. If you have questions or need to change anything once you have paid your reservation please contact the Gulf Wars Reservationist at reservations@gulffwars.org. "
                "\n3. The GW Exchequer must RECEIVE requests for refunds in writing, postmarked or e-mailed no later than your registered date of arrival. Refund requests should be submitted using a Site Fee Refund Request found on the Gulf Wars Registration website and emailed to exchequer@gulfwars.org. "
                "\nAll refund requests for any reason will be processed until February 27, 2026. Requests received by after pre-registration closes will be processed at the discretion of the GW Exchequer and the GW Autocrats. Refund requests made after Gulf Wars starts are not guaranteed to be honored. "
                "\n1. ALL Refunds will be paid via check after the War has ended. A processing fee of $10 per person will be charged to all refunds of PayPal reservations."
            }
        elif type == 'MERCHANT':
            self.detail = {
                "reference": "Gulf Wars XXXIV (2026)",
                "currency_code": "USD",
                "invoice_number": str(get_invoice_number()),
                "invoice_date": datetime.now(pytz.timezone('America/Chicago')).strftime("%Y-%m-%d"),
                "note": "Gulf Wars XXXIV- A war with no enemies! "
                "\nALL INVOICES MUST BE PAID WITHIN 7 DAYS OR THE RESERVATION MAY BE CANCELLED."
                "\nRegistrations will be closed February 21, 2026 with payment due by February 28, 2026.",
                "payment_term": {
                    "term_type": "DUE_ON_DATE_SPECIFIED",
                    "due_date": (datetime.now(pytz.timezone('America/Chicago')) + timedelta(days=7)).strftime("%Y-%m-%d")
                    },
                "memo": "Merchant",
                "terms_and_conditions": "Terms & Conditions (Merchants) "
                "\n1. Please pay invoice by November 19th or your reservation may be cancelled and your merchant space given away. "
                "\n2. If you have questions or need to change anything once you have paid your merchant fees please contact the Gulf Wars Merchantcrat at merchantcrat@gulfwars.org. "
                "\n3. The GW Exchequer must RECEIVE requests for refunds in writing, postmarked or e-mailed no later than February 27, 2026. Refund requests for merchant fees must be accompanied by a Merchant Fee Refund Request available on the Gulf Wars Registration site. After that date, refunds will be issued at the discretion of the Gulf War Exchequer, the Autocrats, and the Merchantcrats. No refunds will be processed after March 13, 2026. "
                "\n4. ALL Refunds will be paid via check to be issued after the War has ended. Merchants will forfeit their Merchant Processing Fee for all refunds."
            }
        elif type == 'EARLYON':
            self.detail = {
                "reference": "Gulf Wars XXXIV (2026)",
                "currency_code": "USD",
                "invoice_number": str(get_invoice_number()),
                "invoice_date": datetime.now(pytz.timezone('America/Chicago')).strftime("%Y-%m-%d"),
                "note": "Gulf Wars XXXIV- A war with no enemies! "
                "\nALL INVOICES MUST BE PAID WITHIN 7 DAYS OR THE RESERVATION MAY BE CANCELLED.  "
                "\nRegistrations will be closed February 21, 2026 with payment due by February 28, 2026.",
                "payment_term": {
                    "term_type": "DUE_ON_DATE_SPECIFIED",
                    "due_date": (datetime.now(pytz.timezone('America/Chicago')) + timedelta(days=7)).strftime("%Y-%m-%d")
                    },
                "memo": "Early-On",
                "terms_and_conditions": "Terms and Conditions (Early-on) "
                "\n1. Your invoice must be paid in full for the full week in order to be eligible for Early-on."
                "\n2. You must have approval from your Department Head and the Autocrat to be allowed on-site before Saturday at noon."
                "\n3. If you have questions or need to change anything once you have paid your reservation please contact the Gulf Wars Reservationist at reservations@gulffwars.org."
            }
        self.invoicer = {
            "business_name": "Society For Creative Anachronism-Gulf Wars, Inc",
            'email_address':'gwincpp@gmail.com',
            # "email_address": "sb-6x1ar45446347@business.example.com",
            "website": "www.gulfwars.org",
        }
        self.primary_recipients = [{"billing_info": {"email_address": invoice_email}}]
        items = []
        for reg in registrations:
            items.extend(reg.get_invoice_items())
        self.items = items


def get_accesstoken():
    # global PAYPAL_API_BASE_URL
    # global PAYPAL_CLIENT_ID
    # global PAYPAL_SECRET
    # global PAYPAL_PAYMENT_WEBHOOK_ID
    # env_vars = EventVariables.query.filter(EventVariables.id==1).first()
    # PAYPAL_API_BASE_URL = env_vars.bas
    # PAYPAL_CLIENT_ID = env_vars.cli 
    # PAYPAL_SECRET = env_vars.sec
    # PAYPAL_PAYMENT_WEBHOOK_ID = env_vars.web
    global access_token
    global access_token_cache
    if access_token is not None and access_token_cache > datetime.now():
        return access_token
    else:
        url = f"{PAYPAL_API_BASE_URL}/v1/oauth2/token"
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
        elif response.status_code != 200:
            raise Exception(response.json())


def create_invoice(registrations, invoice_email, type):
    url = f"{PAYPAL_API_BASE_URL}/v2/invoicing/invoices"

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    new_invoice = PayPal_Invoice(registrations, invoice_email, type)

    data = json.dumps(new_invoice.__dict__)

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        data_dict = response.json()
        return data_dict
    elif response.status_code != 200:
        raise Exception(response.json())


def send_invoice(invoice_id):
    url = f"{PAYPAL_API_BASE_URL}/v2/invoicing/invoices/{invoice_id}/send"

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
    }

    data = '{ "send_to_invoicer": true }'

    response = requests.post(url, headers=headers, data=data)

def cancel_invoice_non_payment(invoice_id):
    url = f"{PAYPAL_API_BASE_URL}/v2/invoicing/invoices/{invoice_id}/cancel"

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
    }

    data = '{ "send_to_invoicer": true, "send_to_recipient": true, "note":"This is to inform you that we have cancelled your invoice and associaited registrations due to non-payment. \nIf you still plan to attend Gulf Wars XXXIV (2026), please reregister at https://gulfwars.org/registration." }'

    response = requests.post(url, headers=headers, data=data)

def cancel_invoice_duplicate(invoice_id):
    url = f"{PAYPAL_API_BASE_URL}/v2/invoicing/invoices/{invoice_id}/cancel"

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
    }

    data = '{ "send_to_invoicer": true, "send_to_recipient": true, "note":"It has come to our attention that a duplicate invoice was issued to you. \nThis is to inform you that we have cancelled this invoice to avoid confusion. \nIf you have questions or concerns, please contact the Gulf Wars Reservationist at reservations@gulfwars.org." }'

    response = requests.post(url, headers=headers, data=data)

def send_reminder(invoice_id):
    url = f"{PAYPAL_API_BASE_URL}/v2/invoicing/invoices/{invoice_id}/remind"

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
    }

    data = '{ "send_to_invoicer": true, "send_to_recipient": true, "note":"This is a reminder that your invoice has not been paid. Please note, it will be cancelled, if not paid in full, as will all registrations associated with this invoice." }'

    response = requests.post(url, headers=headers, data=data)

def get_invoice_number():
    url = f"{PAYPAL_API_BASE_URL}/v2/invoicing/generate-next-invoice-number"

    headers = {
        "Authorization": get_accesstoken(),
        "Content-Type": "application/json",
    }
    data = "{}"

    response = requests.post(url, headers=headers, data=data)

    data_dict = response.json()

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
        "webhook_id": PAYPAL_PAYMENT_WEBHOOK_ID,
        "webhook_event": webhook_event,
    }

    response = requests.post(
        f"{PAYPAL_API_BASE_URL}/v1/notifications/verify-webhook-signature",
        headers=headers,
        data=json.dumps(data),
    )

    data_dict = response.json()

    if data_dict['verification_status'] == "SUCCESS":
        return True
    else:
        return False
