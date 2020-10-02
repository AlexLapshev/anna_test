from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, conint, validator
from datetime import datetime


class BaseTask(BaseModel):
    task_name: str
    task_description: str
    task_finish: Optional[datetime] = None

    @validator('task_name')
    def task_name_length(cls, task_name):
        if len(task_name) > 25 or len(task_name) < 1:
            raise HTTPException(detail='incorrect task name length', status_code=400)
        return task_name

    @validator('task_description')
    def task_description_length(cls, task_description):
        task_description_length = len(task_description)
        if task_description_length > 255 or task_description_length < 5:
            raise HTTPException(detail='incorrect task description length', status_code=400)
        return task_description


class Task(BaseTask):
    task_id: int
    task_created: datetime
    user_id: int
    task_status: str


class TaskChange(BaseTask):
    task_status: conint(gt=0, lt=5)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
