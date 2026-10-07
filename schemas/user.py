from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8)


class UserCredentials(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_name: str
    password: str


class UserRead(BaseModel):
    user_id: int
    user_name: str
