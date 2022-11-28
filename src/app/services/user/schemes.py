from pydantic import BaseModel, validator

from app.services.user.validate import validate_email


class UserBase(BaseModel):
    email: str = "string@gmail.com"
    first_name: str = "Ivan"
    last_name: str = "Grechka"
    age: int = 18

    @validator("email")
    def validate_email(cls, email):
        if validate_email(email):
            return email
        raise ValueError("Email does not correct")

    @validator("age")
    def validate_age(cls, age):
        if age < 0 or age > 100:
            raise ValueError("Age does not correct, should be from 0 to 1000")
        return age


class UserCreateValidators(BaseModel):
    @validator("username", check_fields=False)
    def validate_login(cls, username):
        if len(username) > 30:
            raise ValueError("Username should not have more than 30 symbols ")
        elif len(username) < 8:
            raise ValueError("Username should have more than 8 symbols ")
        return username

    @validator("password", check_fields=False)
    def validate_password(cls, password):
        if len(password) > 30:
            raise ValueError("Password should not have more than 30 symbols ")
        elif len(password) < 8:
            raise ValueError("Password should have more than 8 symbols ")
        return password


class UserCreate(UserBase, UserCreateValidators):
    password: str = "string355"
    username: str = "string355"


class User(UserBase):
    id: int
    username: str
    password: str
    age: int

    class Config:
        orm_mode = True


class UserToken(BaseModel):
    token: str


class UserLogin(BaseModel):
    username: str = "string355"
    password: str = "string355"

    class Config:
        orm_mode = True


class UserPatch(UserCreateValidators):
    username: str = "string355"
    password: str = "string355"
