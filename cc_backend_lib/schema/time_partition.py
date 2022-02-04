
import datetime
from pydantic import BaseModel

class TimePartition(BaseModel):
    start:           datetime.date
    end:             datetime.date
    duration_months: int

    @property
    def duration(self):
        return self.end - self.start
