from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
from config import Config as cfg
from typing import List, Dict, Optional


class JwtSettings(BaseModel):
    authjwt_secret_key: str = cfg.SECRET_KEY


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Store(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    token: str
    name: str
    user_id: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    token: str
    name: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Product(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    title: str
    status: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    email: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}