import uuid
from typing import Optional
from pydantic import BaseModel, Field

class Items(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    email: str = Field(...)
    item_name: str = Field(...)
    quantity: int = Field(...)
    expiry_date: str =Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "1",
                "name": "Don Quixote",
                "email": "don@gmail.com",
                "item_name": "egg",
                "quantity":  10,
                "expiry_date": "2024-10-12"
            }
        }

class ItemUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    item_name: Optional[str]
    quantity: Optional[int]
    expiry_date: Optional[str]

    class Config:
        schema_extra = {
            "example": {
            "name": "Don Quixote",
            "email": "don@gmail.com",
            "item_name": "egg",
            "quantity": 11,
            "expiry_date": "2024-10-12"
            }
        }
        
        
class Clock_In_Records(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    email: str = Field(...)
    location: str = Field(...)
    
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "email": "don@gmail.com",
                "location": "Don Quixote"
            }
        }
        
class Clock_inUpdate(BaseModel):
    email: Optional[str]
    location: Optional[str]
    
    
    class Config:
        schema_extra = {
            "example": {
                "email": "don@gmail.com",
                "location": "Don Quixote"
            }
        }
        
