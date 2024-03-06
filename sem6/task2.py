# Создать веб-приложение на FastAPI, которое будет предоставлять API для
# работы с базой данных пользователей. Пользователь должен иметь
# следующие поля:
# ○ ID (автоматически генерируется при создании пользователя)
# ○ Имя (строка, не менее 2 символов)
# ○ Фамилия (строка, не менее 2 символов)
# ○ Дата рождения (строка в формате "YYYY-MM-DD")
# ○ Email (строка, валидный email)
# ○ Адрес (строка, не менее 5 символов)
import databases
import sqlalchemy
from fastapi import FastAPI
import uvicorn
from typing import List
from models import UserT2, UserInT2
from faker import Faker
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path as PathLib

PathLib(PathLib.cwd() / 'db').mkdir(exist_ok=True)
DATABASE_URL = "sqlite:///db/mydatabase2.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(32)),
    sqlalchemy.Column("last_name", sqlalchemy.String(32)),
    sqlalchemy.Column("birthday", sqlalchemy.Date()),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("address", sqlalchemy.String(128)),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
fake = Faker("ru_RU")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    print("Server connected")
    yield
    await database.disconnect()
    print("Server disconnected")


app = FastAPI(lifespan=lifespan)


@app.post("/users/", response_model=UserT2)
async def create_user(user: UserInT2):
    query = users.insert().values(**user.dict())
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.get("/fake_users/{count}")
async def create_note(count: int):
    for i in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        birthday = datetime.strptime(fake.date(), '%Y-%m-%d')
        email = fake.unique.email()
        address = fake.address()
        query = users.insert().values(first_name=first_name, last_name=last_name, birthday=birthday, email=email,
                                      address=address)
        await database.execute(query)
    return {'message': f'{count} fake users create'}


@app.get("/users/", response_model=List[UserT2])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.put("/users/{user_id}", response_model=UserT2)
async def update_user(user_id: int, new_user: UserInT2):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': 'User deleted'}


if __name__ == "__main__":
    uvicorn.run("task2:app", port=8000, reload=True)
