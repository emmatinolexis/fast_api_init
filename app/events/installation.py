from app.model.installation import Installation
from app.model.user import User


class InstallationCreated:
    def __init__(self,installation:Installation,user:User):
        self.installation = installation
        self.user = user