import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()
subject = "Email Subject"
body = "This is the body of the text message"

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

t_complete = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="max-w-[600px] mx-auto p-5 font-sans bg-gray-50">
        <div class="text-center p-5 bg-blue-600 text-white rounded">
            <h1 class="text-2xl">Transaction Complete</h1>
        </div>
        <div class="text-center p-5 my-5 bg-white rounded shadow-md">
            <p>Your transaction has been completed successfully!</p>
            <div class="mt-4">
                <p class="text-lg">Amount: ₹{amount}</p>
                <p class="text-lg">Type: {type}</p>
            </div>
        </div>
        <p class="text-gray-600">Thank you for using CinemaCloud!</p>
    </div>
</body>
</html>
"""

verification_email = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="max-w-[600px] mx-auto p-5 font-sans bg-gray-50">
        <div class="text-center p-5 bg-blue-600 text-white rounded">
            <h1 class="text-2xl">Email Verification</h1>
        </div>
        <div class="text-center p-5 my-5 bg-white rounded shadow-md">
            <p>Please verify your email by clicking the button below:</p>
            <a href="{verification_link}" class="inline-block px-6 py-3 mt-4 text-white bg-blue-600 rounded hover:bg-blue-700">
                Verify Email
            </a>
            <p class="mt-4 text-sm text-gray-600">Or copy and paste this link in your browser:</p>
            <p class="text-sm text-blue-600 break-all">{verification_link}</p>
        </div>
        <p class="text-gray-600">If you didn't create an account, please ignore this email.</p>
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
