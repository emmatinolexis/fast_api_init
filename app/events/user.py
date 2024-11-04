from app.model.invitation import Invitation
from app.model.user import User
from app.model.role import Role
from app.model.asset import Asset
 




class InviteAccepted:
    def __init__(self,invitation:Invitation):
        self.invitation = invitation




class RoleUpdated:
    def __init__(self,role:Role,user:User):
        self.role = role
        self.user = user
    


class VehicleAssignment:
    def __init__(self,asset:Asset, user:User):
        self.asset = asset
        self.user = user



class VehicleUnassignment:
    def __init__(self,asset:Asset, user:User):
        self.asset = asset
        self.user = user





