from typing import List, Dict
import motor.motor_asyncio
from config import Config as cfg
from models import Store, User


client = motor.motor_asyncio.AsyncIOMotorClient(cfg.DB)
db = client.shopify


async def add_store(name: str, token: str, user_id: str) -> Store:
    store = Store(name=name, token=token, user_id=user_id)
    if hasattr(store, "id"):
        delattr(store, "id")
    ret = await db.stores.insert_one(store.dict(by_alias=True))
    store.id = ret.inserted_id
    return store


async def get_stores() -> List[Store]:
    db_stores = db.stores.find()
    stores = []
    for store in await db_stores.to_list():
        stores.append(Store(**store))
    return stores


async def get_store(user_id) -> Store:
    store = await db.stores.find_one({"user_id": user_id})
    if store:
        return Store(**store)
    raise Exception("Not found")


async def get_store_with_name(name) -> Store:
    store = await db.stores.find_one({"name": name})
    if store:
        return Store(**store)
    raise Exception("Not found")


from bson.objectid import ObjectId


async def update_store(_id: str, values: Dict) -> Store:
    new_values = {"$set": values}
    await db.stores.update_one({"_id": ObjectId(_id)}, new_values)


async def add_user(token, name):
    user = User(token=token, name=name)
    if hasattr(user, "id"):
        delattr(user, "id")
    ret = await db.users.insert_one(user.dict(by_alias=True))
    user.id = ret.inserted_id
    return user


async def get_user_with_token(token) -> User:
    user = await db.users.find_one(token)
    if user:
        return User(**user)
    raise Exception("Not found")