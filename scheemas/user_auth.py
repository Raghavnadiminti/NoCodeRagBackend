from pydantic import BaseModel

class UserCreate(BaseModel):
    email:str 
    name:str 
    password:str 
    mobile_number:str


class UserLogin(BaseModel):
    email:str 
    password:str
