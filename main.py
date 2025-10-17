from pydantic import BaseModel
from fastapi import FastAPI
import random

app = FastAPI()

with open('food.txt', 'r', encoding='utf-8') as f:
    foods = f.read().splitlines()

with open('adjectives.txt', 'r', encoding='utf-8') as f:
    adjectives = f.read().splitlines()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/foods/{id}")
async def read_food(id: int):
    if (id > 2300000 or id < 0):
        return {"error": "Invalid food ID"}
    return {
        "id": id,
        "name": f"{random.seed(id) or random.choice(adjectives)} {random.choice(foods)}"
    }

@app.get("/foods/")
async def read_foods(skip: int = 0, limit: int = 10):
    return { 
        "foods": [
            { 
                "id": i,
                 "name": f"{random.seed(i) or random.choice(adjectives)} {random.choice(foods)}"
             } for i in range(skip,min(skip + limit,2300000))
        ], 
        "total": 2300000 
    }

items = []
class Item(BaseModel):
    name: str
    description: str
    price: float
    tax: float | None = None

@app.get("/items/{id}")
async def read_item(id: int):
    return items[id] if id < len(items) else { "error": "Item not found" }

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return { 
        "items": [
            items[i] for i in range(skip, min(skip + limit, len(items)))
        ], 
        "total": len(items)
    }

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax: 
        item_dict['price_with_tax'] = item.price + item.tax
    items.append(item_dict)
    return item_dict

@app.put("/items/{id}")
async def update_item(id: int, item: Item):
    if id >= len(items):
        return { "error": "Item not found" }
    item_dict = item.model_dump()
    if item.tax: 
        item_dict['price_with_tax'] = item.price + item.tax
    items[id] = item_dict
    return item_dict
