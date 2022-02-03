
from typing import Optional
import datetime
from pydantic import BaseModel, validator, ConstrainedInt
from pydantic import HttpUrl

class HttpCode(ConstrainedInt):
    ge = 100
    le = 500

class HttpError(BaseModel):
    http_code: HttpCode
    message:   str               = ""
    url:       Optional[HttpUrl]
    time:      Optional[datetime.datetime] = None

    @validator("time")
    def set_time(cls, time: Optional[datetime.datetime]):
        return time if time is not None else datetime.datetime.now()
