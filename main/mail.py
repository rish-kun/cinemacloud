import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()
subject = "Email Subject"
body = "This is the body of the text message"
# recipients = ["f20240545@pilani.bits-pilani.ac.in",
#               "f20240606@pilani.bits-pilani.ac.in"]
email_body = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="max-w-[600px] mx-auto p-5 font-sans bg-gray-50">
        <div class="text-center p-5 bg-blue-600 text-white rounded">
            <h1 class="text-2xl">Your OTP Code</h1>
        </div>
        <div class="text-center p-5 my-5 bg-white rounded shadow-md">
            <p>Here's your one-time verification code:</p>
            <div class="text-4xl tracking-widest text-blue-600 font-bold">{otp}</div>
            <p>This code will expire in 10 minutes.</p>
        </div>
        <p class="text-gray-600">If you didn't request this code, please ignore this email.</p>
    </div>
</body>
</html>
"""


def send_email(subject, body, recipients):
    sender = "python.mailverify@gmail.com"
    password = os.getenv("EMAIL_PASSWORD")
    msg = MIMEText(body, "html")
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
    return True


# send_email(subject, body, sender, recipients, password)


# def verification_email(subject, body, user):