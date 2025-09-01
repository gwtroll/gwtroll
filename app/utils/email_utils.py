from app import mail, qrcode
from flask_mail import Message
from flask import url_for, copy_current_request_context
import base64, binascii
import threading


# hold = "<p>To apply for Early On please use the following link: <a href="
#         + url_for("earlyon.createearlyon", regid=reg.id, _external=True)
#         + ">APPLY FOR EARLY ON</a></p>"
#         "<p>All staff can have 1 FREE ADULT RIDER - Additional Early On riders will cost $15 per adult.</p>"
#         "<p>If you owe any money for additional riders, you will receive a seperate invoice.</p>"
#         "<p>Once the Department Head and Autocrats have approved your application, as well as paid any balance, you will receive an email confirming your Early On Approval.</p>"
#         "<p>{INSERT RULES/INFO/STATEMENTS}</p>"
#         "<p>{INSERT IF YOU RECEIVED THIS IN ERROR MESSAGE}</p>"
#         "<p>In Service,<br/>"
#         "Salim Al'Hahlil<br/>"
#         "Testing SMTP Deputy</p>"

def send_async_mail(message):

    @copy_current_request_context
    def send_message(message):
        mail.send(message)

    sender = threading.Thread(name="mail_sender", target=send_message, args=(message,))
    sender.start()


def send_confirmation_email(recipient, regs):
    msg = Message(
        subject="Gulf Wars Registration Confirmation",
        recipients=[recipient],
    )

    regs_string = ""
    for reg in regs:
        regs_string += f"<tr><td style='border: 1px solid black; border-collapse: collapse;'>{reg.fname} {reg.lname}</td><td style='border: 1px solid black; border-collapse: collapse;'>{reg.scaname}</td><td style='border: 1px solid black; border-collapse: collapse;'>{reg.mbr_num}</td><td style='border: 1px solid black; border-collapse: collapse;'>{reg.expected_arrival_date}</td><td style='border: 1px solid black; border-collapse: collapse;'>{reg.id}</td><tr>"

    msg.html = (
        "<p>Greetings,</p>"
        "<p>Thank you for registering the following individual(s) for Gulf Wars XXXIV (2026)!</p>"
        "<table style='border: 1px solid black; border-collapse: collapse;'>"
        "<tr>"
        "<th style='border: 1px solid black; border-collapse: collapse;'><b>Mundane Name</b></th>"
        "<th style='border: 1px solid black; border-collapse: collapse;'><b>SCA Name</b></th>"
        "<th style='border: 1px solid black; border-collapse: collapse;'><b>Member Number</b></th>"
        "<th style='border: 1px solid black; border-collapse: collapse;'><b>Arrival Date</b></th>"
        "<th style='border: 1px solid black; border-collapse: collapse;'><b>Registration ID</b></th>"
        "</tr>"
        +regs_string+
        "</table>"
        "<p>You will receive your site fee invoice within 3 days of site registration opening for everyone. Expect to see it by 11/3/2025. Once received, if not paid within seven (7) days, all registrations will be cancelled and you will need to reregister for your site fees.</p>"
        "<p>Once paid, each registrant will receive an individual email with their confirmation, and their FastPass QR Code to use for entry. They will receive a reminder email closer to Gulf Wars to look for the previous email.</p>"
        "<p>If you need to request Early-On access to the site, you will receive instructions once your registration invoice has been paid in-full.</p>"
    )
    send_async_mail(msg)


def send_fastpass_email(recipient, reg):
    qrcode_str = qrcode(url_for("troll.reg", regid=reg.id), border=1)
    msg = Message(
        subject="Gulf Wars Fast Pass",
        recipients=[recipient],
    )

    qrcode_str = qrcode_str[22:]
    image = base64.b64decode(qrcode_str, validate=True)

    msg.attach(
        "fastpass.png",
        "image/png",
        image,
        "inline",
        headers=[
            ["Content-ID", "<fastpass>"],
        ],
    )

    msg.html = (
        "<p>Greetings,</p>"
        "<p>Welcome to Fast Pass! Please print this and bring it with you to Gulf Wars. If everyone in your vehicle has this with them, you will be able to participate in Fast Pass Troll. Please follow the signs to Troll.  You will be asked to show this letter, photo ID, and proof of membership if you are a member. Those not on fast pass will park and walk in to troll. If EVERYONE in your vehicle has their letter printed, you will be flagged through to the fast pass lanes. The troll will scan this letter, go over the waiver with you, and give you your site token. You may then proceed to your campsite. You will not be able to leave your vehicle once in the fast pass lane.</p>"
        "<p>Fast Pass is only open Opening Saturday 1pm until dark. If you do not have this letter, you will need to park and walk inside. Troll will attempt to scan the QR code off a mobile device if it is not printed.</p>"
        "<br/><br/>"
        "<p>Registration ID: " + str(reg.id) + "<br/>"
        "Name: " + reg.fname + " " + reg.lname + "<br/>"
        "Arrival Date: " + str(reg.expected_arrival_date) + "</p>"
        '<img src="cid:fastpass" alt="Fast Pass QR Code">'
    )

    send_async_mail(msg)


def send_merchant_confirmation_email(recipient, merchant):
    msg = Message(
        subject="Gulf Wars - Merchant Application Confirmation",
        recipients=[recipient],
    )

    msg.html = (
        "<p>Greetings,</p>"
        "<p>Your Merchant Application for Gulf Wars XXXIV has been successfully submitted. You will receive another email once you are approved.</p>"
        "<ul>"
        "<li>Application review will start in October.</li>"
        "<li>Invoices can’t go out until October currently. We will keep you updated on any changes.</li>"
        "</ul>"
        "<p>If you have any questions or need to submit further information please contact the Merchantcrats at <a href='mailto:merchantcrat@gulfwars.org'>merchantcrat@gulfwars.org</a></p>"
        "<p>In Service,<br/>"
        "Master Odhrán macc Corbáin<br/>"
        "THL Dante Matteo Ricci</p>"
        "<br/><br/>"
    )
    send_async_mail(msg)


def send_merchant_approval_email(recipient, merchant):
    qrcode_str = qrcode(
        url_for("merchant.merchant_checkin", merchantid=merchant.id), border=1
    )
    msg = Message(
        subject="Gulf Wars - Merchant Approval",
        recipients=[recipient],
    )

    qrcode_str = qrcode_str[22:]
    image = base64.b64decode(qrcode_str, validate=True)

    msg.attach(
        "fastpass.png",
        "image/png",
        image,
        "inline",
        headers=[
            ["Content-ID", "<fastpass>"],
        ],
    )

    msg.html = (
        "<p>Greetings,</p>"
        "<p>Your Merchant Application has been Approved for Gulf Wars XXXIV! We are excited to have you join us this March. Be on the lookout for your invoices from Gulf Wars PayPal team and get those taken care of.</p>"
        "<p><b>Invoices can’t go out until October currently. We will keep you updated on any changes.</b></p>"
    )
    (
        "<p>If you have any questions or need further information please contact the Merchantcrats at <a href='mailto:merchantcrat@gulfwars.org'>merchantcrat@gulfwars.org</a></p>"
        "<p>In Service,<br/>"
        "Master Odhrán macc Corbáin<br/>"
        "THL Dante Matteo Ricci</p>"
        "<br/><br/>"
        "<p>Merchant ID: " + str(merchant.id) + "<br/>"
        "Name: " + merchant.fname + " " + merchant.lname + "<br/>"
        "Business Name: " + merchant.business_name + "<br/>"
        "Arrival Date: " + str(merchant.estimated_date_of_arrival) + "</p>"
        '<img src="cid:fastpass" alt="Fast Pass QR Code">'
    )

    send_async_mail(msg)
