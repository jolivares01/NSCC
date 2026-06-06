from pydantic import BaseModel, validator

class LoginRequest(BaseModel):
    username: str
    password: str
'''
    @validator('username')
    def username_to_upper(cls, v):
        return v.upper()
'''      