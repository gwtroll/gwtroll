from app import mail, qrcode
from flask_mail import Message
from flask import url_for
import base64, binascii

def send_confirmation_email(recipient, reg):
    qrcode_str = qrcode(url_for('troll.reg', regid=reg.id))
    msg = Message(
        subject="Gulf Wars Fast Pass",
        sender="carl.cox.primary@gmail.com",
        recipients=[recipient],
    )

    print(qrcode_str)

    qrcode_str = qrcode_str[22:]
    image = base64.b64decode(qrcode_str, validate=True)

    msg.attach('fastpass.png','image/png',image, 'inline', headers=[['Content-ID','<fastpass>'],])
    
    msg.html = "<p>Greetings,</p>" \
    "<p>Welcome to Fast Pass! Please print this and bring it with you to Gulf Wars. If everyone in your vehicle has this with them, you will be able to participate in Fast Pass Troll. Please follow the signs to Troll.  You will be asked to show this letter, photo ID, and proof of membership if you are a member. Those not on fast pass will park and walk in to troll. If EVERYONE in your vehicle has their letter printed, you will be flagged through to the fast pass lanes. The troll will scan this letter, go over the waiver with you, and give you your site token. You may then proceed to your campsite. You will not be able to  leave your vehicle once in the fast pass lane.</p>" \
    "<p>Fast Pass is available opening day only. Saturday 1p-9p.  If you do not have this letter, you will need to park and walk inside.  Troll will attempt to scan the QR code off a mobile device if it is not printed.</p>" \
    "<p>In Service,<br/>" \
    "Salim Al'Kahlil<br/>" \
    "Testing SMTP Deputy</p>" \
    "<br/><br/>" \
    "<p>RegID: "+str(reg.id)+"<br/>" \
    "Name: "+reg.fname+" "+reg.lname+"<br/>" \
    "Arrival Date: "+str(reg.expected_arrival_date)+"</p>" \
    "<img src=\"cid:fastpass\" alt=\"Fast Pass QR Code\">"
    
    mail.send(msg)

def send_merchant_confirmation_email(recipient, merchant):
    msg = Message(
        subject="Gulf Wars - Merchant Application Confirmation",
        sender="carl.cox.primary@gmail.com",
        recipients=[recipient],
    )
    
    msg.html = "<p>Greetings,</p>" \
    "<p>We have received your Merchant Application</p>" \
    "<p>In Service,<br/>" \
    "Salim Al'Kahlil<br/>" \
    "Testing SMTP Deputy</p>" \
    "<br/><br/>" \

    mail.send(msg)

def send_merchant_approval_email(recipient, merchant):
    qrcode_str = qrcode(url_for('merchant.merchant_checkin', merchantid=merchant.id))
    msg = Message(
        subject="Gulf Wars - Merchant Approval",
        sender="carl.cox.primary@gmail.com",
        recipients=[recipient],
    )

    print(qrcode_str)

    qrcode_str = qrcode_str[22:]
    image = base64.b64decode(qrcode_str, validate=True)

    msg.attach('fastpass.png','image/png',image, 'inline', headers=[['Content-ID','<fastpass>'],])
    
    msg.html = "<p>Greetings,</p>" \
    "<p>You have been approved to merchant ay Gulf Wars!</p>" \
    "<p>In Service,<br/>" \
    "Salim Al'Kahlil<br/>" \
    "Testing SMTP Deputy</p>" \
    "<br/><br/>" \
    "<p>RegID: "+str(merchant.id)+"<br/>" \
    "Name: "+merchant.fname+" "+merchant.lname+"<br/>" \
    "Arrival Date: "+str(merchant.estimated_date_of_arrival)+"</p>" \
    "<img src=\"cid:fastpass\" alt=\"Fast Pass QR Code\">"
    
    mail.send(msg)

def send_merchant_denial_email(recipient, merchant):
    msg = Message(
        subject="Gulf Wars - Merchant Denied",
        sender="carl.cox.primary@gmail.com",
        recipients=[recipient],
    )
    
    msg.html = "<p>Greetings,</p>" \
    "<p>You have been denied to merchant ay Gulf Wars!</p>" \
    "<p>In Service,<br/>" \
    "Salim Al'Kahlil<br/>" \
    "Testing SMTP Deputy</p>" \
    
    mail.send(msg)