from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Owner_schema(BaseModel):
    fullname: str
    email: EmailStr

class OwnerResponse(Owner_schema):
    id: int = 1

    class Config():
        from_attributtes = True

class CatBase(BaseModel):
    nick: str = Field('Simon', min_length=3, max_length=25)
    age: int = Field(1, ge=1, le=30)
    vaccinated: Optional[bool] = False 
    

class Cat_schema(CatBase):
    owner_id: int = Field(1, ge=1)

class CatsResponse(Cat_schema):
    id: int =1
    owner: OwnerResponse

    class Config:
        from_attribute = True