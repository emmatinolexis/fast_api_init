import os
def read_email_template():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_directory, '..', 'templates', 'email-template.html')
    with open(template_path, "r") as file:
        return file.read()