from app import mail, qrcode
from flask_mail import Message
from flask import url_for
import base64, binascii

def send_confirmation_email(recipient, reg):
    qrcode_str = qrcode(url_for('troll.reg', regid=reg.regid))
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
    "<p>RegID: "+str(reg.regid)+"<br/>" \
    "Name: "+reg.fname+" "+reg.lname+"<br/>" \
    "Arrival Date: "+reg.rate_date+"</p>" \
    "<img src=\"cid:fastpass\" alt=\"Fast Pass QR Code\">"
    
    mail.send(msg)