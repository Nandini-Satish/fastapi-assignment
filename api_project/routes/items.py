from fastapi import APIRouter,Query, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List,Optional
from datetime import date
from bson import ObjectId
from database import item_helper
from requests import request
from models import Items, ItemUpdate

router = APIRouter()

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    item_data = item.dict()
    item_data["insert_date"] = datetime.utcnow()
    result = await db.items.insert_one(item_data)
    return {**item_data, "id": str(result.inserted_id)}

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    print(f"Received item_id: {item_id}")  # Add this line
    item = await db.items.find_one({"_id": ObjectId(item_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_dict(item)
    # return item_dict(item)


@app.get("/items/filter", response_model=List[Item])
async def filter_items(email: Optional[str] = None,expiry_date: Optional[datetime] = None,insert_date: Optional[datetime] = None,quantity: Optional[int] = None):
    query = {}

    # Construct the query based on provided filters
    if email:
        query["email"] = email
    if expiry_date:
        query["expiry_date"] = {"$gt": expiry_date}
    if insert_date:
        query["insert_date"] = {"$gt": insert_date}
    if quantity is not None:
        query["quantity"] = {"$gte": quantity}

    items = []

    # Fetch items from the database
    async for item in db.items.find(query):
        items.append(item_dict(item))

    return items

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await db.items.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item deleted"}

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    update_data = item.dict(exclude_unset=True)
    result = await db.items.update_one({"_id": ObjectId(item_id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = await db.items.find_one({"_id": ObjectId(item_id)})
    return item_dict(updated_item)