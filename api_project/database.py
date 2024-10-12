from bson import ObjectId


def item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),  # Convert ObjectId to string for FastAPI
        "name": item["name"],
        "email": item["email"],
        "item_name": item["item_name"],
        "quantity": item["quantity"],
        "expiry_date": item["expiry_date"]
        
    }
