from app.model.invitation import Invitation
from app.model.user import User
from app.model.role import Role
 




class InviteAccepted:
    def __init__(self,invitation:Invitation):
        self.invitation = invitation




class RoleUpdated:
    def __init__(self,role:Role,user:User):
        self.role = role
        self.user = user
    




