from pydantic import BaseModel
from datetime import datetime


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
