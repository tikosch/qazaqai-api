from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class SignUpRequest(BaseModel):
    Username: str = Field(alias="username")
    Email: EmailStr = Field(alias="email")
    Password: str = Field(alias="password")
    Referral: Optional[str] = Field(default=None, alias="referral")

    class Config:
        allow_population_by_field_name = True

from pydantic import BaseModel, Field, EmailStr

class SignUpResponse(BaseModel):
    Username: str = Field(alias="username")
    Email: EmailStr = Field(alias="email")

    class Config:
        allow_population_by_field_name = True



class SignInRequest(BaseModel):
    Email: EmailStr = Field(alias="email")
    Password: str = Field(alias="password")

    class Config:
        allow_population_by_field_name = True

class SignInResponse(BaseModel):
    token: str

    class Config:
        allow_population_by_field_name = True
