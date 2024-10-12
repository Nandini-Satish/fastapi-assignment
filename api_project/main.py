from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

app = FastAPI()
client = AsyncIOMotorClient("mongodb+srv://Nandini_1:RDPsXmSCQwDmkXDi@cluster0.rcmql.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Update with your MongoDB connection string
db = client.fastapi_assignment

# Pydantic models
class Item(BaseModel):
    name: str
    email: str
    item_name: str
    quantity: int
    expiry_date: datetime

class ClockInRecord(BaseModel):
    email: str
    location: str

# Helper functions
def item_dict(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "email": item["email"],
        "item_name": item["item_name"],
        "quantity": item["quantity"],
        "expiry_date": item["expiry_date"],
        "insert_date": item["insert_date"],
    }

def clock_in_record_dict(record) -> dict:
    return {
        "id": str(record["_id"]),
        "email": record["email"],
        "location": record["location"],
        "insert_datetime": record["insert_datetime"],
    }

# CRUD APIs for Items
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

# CRUD APIs for Clock-In Records
@app.post("/clock-in", response_model=ClockInRecord)
async def create_clock_in(record: ClockInRecord):
    record_data = record.dict()
    record_data["insert_datetime"] = datetime.utcnow()
    result = await db.clock_in_records.insert_one(record_data)
    return {**record_data, "id": str(result.inserted_id)}

@app.get("/clock-in/{record_id}", response_model=ClockInRecord)
async def read_clock_in(record_id: str):
    record = await db.clock_in_records.find_one({"_id": ObjectId(record_id)})
    if record is None:
        raise HTTPException(status_code=404, detail="Clock-in record not found")
    return clock_in_record_dict(record)

@app.get("/clock-in/filter", response_model=List[ClockInRecord])
async def filter_clock_ins(email: Optional[str] = None,location: Optional[str] = None,insert_datetime: Optional[datetime] = None):
    query = {}
    if email:
        query["email"] = email
    if location:
        query["location"] = location
    if insert_datetime:
        query["insert_datetime"] = {"$gt": insert_datetime}

    records = []
    async for record in db.clock_in_records.find(query):
        records.append(clock_in_record_dict(record))
    return records

@app.delete("/clock-in/{record_id}")
async def delete_clock_in(record_id: str):
    result = await db.clock_in_records.delete_one({"_id": ObjectId(record_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Clock-in record not found")
    return {"detail": "Clock-in record deleted"}

@app.put("/clock-in/{record_id}", response_model=ClockInRecord)
async def update_clock_in(record_id: str, record: ClockInRecord):
    update_data = record.dict(exclude_unset=True)
    result = await db.clock_in_records.update_one({"_id": ObjectId(record_id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Clock-in record not found")
    updated_record = await db.clock_in_records.find_one({"_id": ObjectId(record_id)})
    return clock_in_record_dict(updated_record)

# MongoDB Aggregation Example
@app.get("/items/aggregation")
async def aggregate_items():
    pipeline = [
        {
            "$group": {
                "_id": "$email",
                "count": {"$sum": 1}
            }
        }
    ]
    result = await db.items.aggregate(pipeline).to_list(length=None)
    return result
