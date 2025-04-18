import motor.motor_asyncio
from config import DB_URI, DB_NAME, COLLECTION_NAME

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]
users = db[COLLECTION_NAME]

async def add_user(user_id):
    user = await users.find_one({"_id": user_id})
    if not user:
        await users.insert_one({"_id": user_id})
        return True
    return False

async def remove_watermark(user_id):
    await users.update_one({"_id": user_id}, {"$unset": {"logo": "", "position": ""}})

async def set_position(user_id, position):
    await users.update_one({"_id": user_id}, {"$set": {"position": position}}, upsert=True)

async def get_position(user_id):
    user = await users.find_one({"_id": user_id})
    return user.get("position") if user and "position" in user else None

async def user_logo(user_id):
    user = await users.find_one({"_id": user_id})
    return user.get("logo") if user and "logo" in user else None
