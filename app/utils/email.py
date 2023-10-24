import os
from fastapi import FastAPI
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def read_email_template():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_directory, '..', 'templates', 'email-template.html')
    with open(template_path, "r") as file:
        return file.read()
    
def send_email(subject, recipient, message):
    try:
        # Create an SMTP connection to the Mailtrap server
        server = smtplib.SMTP(os.environ.get('MAIL_HOST'), os.environ.get('MAIL_PORT'))

        # Login to the Mailtrap server
        server.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))

        # Create an email message
        msg = MIMEMultipart()
        msg["From"] = os.environ.get('MAIL_FROM')
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Send the email
        server.sendmail(os.environ.get('MAIL_USERNAME'), recipient, msg.as_string())

        # Close the SMTP connection
        server.quit()

    except Exception as e:
        return {"message": f"Failed to send email: {str(e)}"}