# Создать API для управления списком задач.
# Каждая задача должна содержать поля "название", "описание" и "статус" (выполнена/не выполнена).
# API должен позволять выполнять CRUD операции с задачами.
# Напишите API для управления списком задач. Для этого создайте модель Task
# со следующими полями:
# ○ id: int (первичный ключ)
# ○ title: str (название задачи)
# ○ description: str (описание задачи)
# ○ done: bool (статус выполнения задачи)
# API должно поддерживать следующие операции:
# ○ Получение списка всех задач: GET /tasks/
# ○ Получение информации о конкретной задаче: GET /tasks/{task_id}/
# ○ Создание новой задачи: POST /tasks/
# ○ Обновление информации о задаче: PUT /tasks/{task_id}/
# ○ Удаление задачи: DELETE /tasks/{task_id}/
# Для валидации данных используйте параметры Field модели Task.
# Для работы с базой данных используйте SQLAlchemy и модуль databases.

import databases
import sqlalchemy
from fastapi import FastAPI, Path
from typing import List
from models import TaskT3, TaskInT3
import uvicorn
from faker import Faker
from pathlib import Path as PathLib
from contextlib import asynccontextmanager
from random import choice

PathLib(PathLib.cwd() / 'db').mkdir(exist_ok=True)
DATABASE_URL = "sqlite:///db/mydatabase3.db"
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

tasks = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(32)),
    sqlalchemy.Column("description", sqlalchemy.String(128)),
    sqlalchemy.Column("done", sqlalchemy.Boolean()),
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


@app.post("/tasks/", response_model=TaskT3)
async def create_task(task: TaskInT3):
    query = tasks.insert().values(**task.dict())
    last_record_id = await database.execute(query)
    return {**task.dict(), "id": last_record_id}


@app.get("/fake_tasks/{count}")
async def create_fake_tasks(count: int):
    for i in range(count):
        title = fake.text(max_nb_chars=32)
        description = fake.text(max_nb_chars=128)
        done = choice([True, False])
        query = tasks.insert().values(title=title, description=description, done=done)
        await database.execute(query)
    return {'message': f'{count} fake tasks created'}


@app.get("/tasks/", response_model=List[TaskT3])
async def read_tasks():
    query = tasks.select()
    return await database.fetch_all(query)


@app.get("/tasks/{task_id}", response_model=TaskT3)
async def read_task(task_id: int = Path(..., gt=0)):
    query = tasks.select().where(tasks.c.id == task_id)
    return await database.fetch_one(query)


@app.put("/tasks/{task_id}", response_model=TaskT3)
async def update_task(task_id: int, new_task: TaskInT3):
    query = tasks.update().where(tasks.c.id == task_id).values(**new_task.dict())
    await database.execute(query)
    return {**new_task.dict(), "id": task_id}


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int = Path(..., gt=0)):
    query = tasks.delete().where(tasks.c.id == task_id)
    res = await database.execute(query)
    return {'message': 'Task deleted'} if res else {'message': f"Task not found with {task_id} id"}


if __name__ == "__main__":
    uvicorn.run("task3_4:app", port=8000, reload=True)
