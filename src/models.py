from pydantic import BaseModel
from datetime import datetime


class RegisterUserRequest(BaseModel):
    name: str
    surname: str
    age: int


class UserModel(BaseModel):
    id: int
    name: str
    surname: str
    age: int

    class Config:
        orm_mode = True


class CityModel(BaseModel):
    id: int
    name: str
    weather: str


class PicnicModel(BaseModel):
    id: int
    city: str
    time: datetime


class RegisterUser(BaseModel):
    user_id: int
    picnic_id: int


class PicnicRegistrationModel(BaseModel):
    id: int
    user_surname: str
    picnic_id: int
