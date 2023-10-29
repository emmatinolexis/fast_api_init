import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

def read_email_template():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_directory, '..', 'templates', 'email-template.html')
    with open(template_path, "r") as file:
        return file.read()
    
def send_email(subject, recipient, email, message, token=""):
    try:
        # Create an SMTP connection to the Mailtrap server
        server = smtplib.SMTP("sandbox.smtp.mailtrap.io", "2525")

        # Load the email template from a file
        env = Environment(loader=FileSystemLoader('app/templates'))
        template = env.get_template('email-template.html')

        # Login to the Mailtrap server
        server.login("3ac816258e1993", "d9e1b01067c879")

        # Create the email message using the template
        message_data = template.render(recipient_name=recipient, message=message, verify_token = token)

        # Create an email message
        msg = MIMEMultipart()
        msg["From"] = "no-reply@mvtracking.com"
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(message_data, 'html'))

        # Send the email
        server.sendmail("3ac816258e1993", email, msg.as_string())

        # Close the SMTP connection
        server.quit()

        return {"message": "mail sent"}

    except Exception as e:
        return {"message": f"Failed to send email: {str(e)}"}