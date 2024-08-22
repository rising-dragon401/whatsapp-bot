from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    customer = "customer"

class AdminUserPermission(str, Enum):
    admin = "admin"
    normal = "normal"
