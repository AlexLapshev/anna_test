from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class BaseTask(BaseModel):
    task_name: str
    task_description: str
    task_finish: datetime


class Task(BaseTask):
    task_id: int
    task_created: datetime
    user_id: int
    task_status: str


class TaskChange(BaseTask):
    task_status: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
