from typing import Annotated
from datetime import timedelta

from pydantic import BaseModel, Field
from fastapi import Body, Depends, FastAPI, Path
import random

from auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()

with open('food.txt', 'r', encoding='utf-8') as f:
    foods = f.read().splitlines()

with open('adjectives.txt', 'r', encoding='utf-8') as f:
    adjectives = f.read().splitlines()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(login_data: LoginRequest):
    """Login endpoint that accepts any username and password and returns a JWT token."""
    access_token = create_access_token(
        username=login_data.username,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"token": access_token}


@app.get("/foods/{id}")
async def read_food(id: int, _username: str = Depends(verify_token)):
    if (id > 2300000 or id < 0):
        return {"error": "Invalid food ID"}
    return {
        "id": id,
        "name": f"{random.seed(id) or random.choice(adjectives)} {random.choice(foods)}"
    }

@app.get("/foods/")
async def read_foods(skip: int = 0, limit: int = 10, _username: str = Depends(verify_token)):
    return { 
        "foods": [
            { 
                "id": i,
                 "name": f"{random.seed(i) or random.choice(adjectives)} {random.choice(foods)}"
             } for i in range(skip,min(skip + limit,2300000))
        ], 
        "total": 2300000 
    }

class Item(BaseModel):
    name: str
    description: str | None = Field(default=None, title="The description of the item", max_length=300)
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None

items = [
    Item(name="Item1", description="The first item", price=10.5, tax=1.5)
]

@app.get("/items/{id}")
async def read_item(id: int):
    return { "id": id, "item": items[id] } if id < len(items) else { "error": "Item not found" }

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return { 
        "items": [
            { "id": i, "item": items[i] } for i in range(skip, min(skip + limit, len(items)))
        ], 
        "total": len(items)
    }

@app.post("/items/")
async def create_item(item: Item):
    items.append(item)
    dump = item.model_dump()
    if item.tax:
        dump.update({"price_with_tax": item.price + item.tax})
    return { "id": len(items) - 1, "item": dump }

@app.put("/items/{id}")
async def update_item(id: int, item: Annotated[Item, Body(embed=True)]):
    if id >= len(items):
        return { "error": "Item not found" }
    results = { "id": id, "item": item }
    items[id] = item
    return results
