from pydantic import BaseModel


class AccountCreate(BaseModel):
    name: str
    account_type: str
    institution: str | None = None


class AccountRead(AccountCreate):
    id: int

    class Config:
        from_attributes = True
