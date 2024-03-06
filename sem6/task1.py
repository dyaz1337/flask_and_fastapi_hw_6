# Разработать API для управления списком пользователей с
# использованием базы данных SQLite. Для этого создайте
# модель User со следующими полями:
# ○ id: int (идентификатор пользователя, генерируется
# автоматически)
# ○ username: str (имя пользователя)
# ○ email: str (электронная почта пользователя)
# ○ password: str (пароль пользователя)
import databases
import sqlalchemy
from fastapi import FastAPI, Path
from typing import List
from models import UserT1, UserInT1
import uvicorn
from faker import Faker
from pathlib import Path as PathLib
from contextlib import asynccontextmanager

PathLib(PathLib.cwd() / 'db').mkdir(exist_ok=True)
DATABASE_URL = "sqlite:///db/mydatabase.db"
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("password", sqlalchemy.String(64)),
)
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

fake = Faker('ru_Ru')


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    print("Server connected")
    yield
    await database.disconnect()
    print("Server disconnected")


app = FastAPI(lifespan=lifespan)


@app.post("/users/", response_model=UserT1)
async def create_user(user: UserInT1):
    query = users.insert().values(username=user.username, email=user.email, password=user.password)
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.get("/fake_users/{count}")
async def create_fake_users(count: int):
    for i in range(count):
        username = fake.name()
        email = fake.unique.email()
        password = fake.password()
        query = users.insert().values(username=username, email=email, password=password)
        await database.execute(query)
    return {'message': f'{count} fake users create'}


@app.get("/users/", response_model=List[UserT1])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.put("/users/{user_id}", response_model=UserT1)
async def update_user(user_id: int, new_user: UserInT1):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int = Path(..., gt=0)):
    query = users.delete().where(users.c.id == user_id)
    res = await database.execute(query)
    return {'message': 'User deleted'} if res else {'message': f"User not found with {user_id} id"}


if __name__ == "__main__":
    uvicorn.run("task1:app", port=8000, reload=True)
