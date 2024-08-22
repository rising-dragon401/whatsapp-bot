from datetime import datetime
from typing import Annotated, Any, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr
from typing import Optional
from database.models.common import AdminUserPermission

class BotManager:
    def __init__(self, id, email, name, avatar, botCount, permission):
        self.id = id
        self.email = email
        self.name = name
        self.avatar = avatar
        self.botCount = botCount
        self.permission = permission

class AdminUserSignin(BaseModel):
    email: str
    password: str

class AdminUserSignup(BaseModel):
    email: str
    name: str
    password: str

class AdminUserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    permission: str = AdminUserPermission.normal

class AdminUserOut(AdminUserUpdate):
    email: Annotated[str, Indexed(EmailStr, unique=True)]
    botCount: int | None = 0
    disabled: bool = False

class AdminUserDocument(Document, AdminUserOut):
    password: str
    email_confirmed_at: datetime | None = None

    class Settings:
        name = "adminusers"

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def __str__(self) -> str:
        return self.email
    
    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AdminUserDocument):
            return self.email == other.email
        return False

    @property
    def created(self) -> datetime | None:
        return self.id.generation_time if self.id else None

    @property
    def jwt_subject(self) -> dict[str, Any]:
        return {"name": self.name, "email": self.email, "permission": self.permission, "id": str(self.id)}

    @classmethod
    async def by_email(cls, email: str) -> Optional["AdminUserDocument"]:
        return await cls.find_one(cls.email == email)
    
    def update_email(self, new_email: str) -> None:
        self.email = new_email

async def read_all_adminusers(admin_id: str, permission: str) -> list[AdminUserDocument]:
    if permission == AdminUserPermission.admin:
        return await AdminUserDocument.find_all().to_list()
    else:
        return await AdminUserDocument.find({"admin_id": admin_id}).to_list()

async def increase_botcount(admin_id: str) -> None:
    adminUser = await AdminUserDocument.get(admin_id)
    if (adminUser):
        await adminUser.update({"$set": {"botCount": adminUser.botCount+1}})

async def decrease_botcount(admin_id: str) -> None:
    adminUser = await AdminUserDocument.get(admin_id)
    if (adminUser):
        await adminUser.update({"$set": {"botCount": adminUser.botCount-1}})
