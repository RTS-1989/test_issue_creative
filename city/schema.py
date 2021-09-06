from pydantic import BaseModel


class CityModel(BaseModel):
    id: int
    name: str
    weather: str
