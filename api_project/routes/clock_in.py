from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime
from models import ClockInRecord
from database import clock_in_collection  # Make sure your MongoDB collection is defined

router1 = APIRouter()

# Helper function to convert MongoDB document to Pydantic model
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
