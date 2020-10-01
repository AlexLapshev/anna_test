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


class TaskChange(BaseModel):
    task_name: Optional[str]
    task_description: Optional[str]
    task_finish: Optional[datetime]
    task_status: Optional[int]
