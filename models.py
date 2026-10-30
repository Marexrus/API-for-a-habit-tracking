from pydantic import BaseModel

class Habit(BaseModel):
  name: str
  color: str
  period_type: str | None = None
  period: int
  date_start: str
