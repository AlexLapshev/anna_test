from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator
from datetime import datetime

STATUSES = ['новая', 'запланированная', 'в работе', 'завершённая']


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
    def task_finish_date(cls, task_description):
        task_description_length = len(task_description)
        if task_description_length > 255 or task_description_length < 5:
            raise HTTPException(detail='incorrect task description length', status_code=400)
        return task_description


class TaskStatus(BaseModel):
    task_status: str

    @validator('task_status')
    def task_status_validate(cls, task_status):
        task_status = task_status.lower()
        if task_status not in STATUSES:
            raise HTTPException(detail='incorrect task status', status_code=400)
        return task_status


class Task(BaseTask, TaskStatus):
    task_id: int
    task_created: datetime
    user_id: int


class TaskChange(BaseTask, TaskStatus):
    pass


class TaskOperation(BaseModel):
    task_id: int
    user_id: int
    task_operation: str
    prev_value: str
    date_change: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


