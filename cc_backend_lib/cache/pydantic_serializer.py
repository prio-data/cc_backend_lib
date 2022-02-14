
import json
from pydantic import BaseModel
from . import cache_serializer

class PydanticSerializer(cache_serializer.CacheSerializer[BaseModel]):

    def __init__(self, model: BaseModel):
        self._model = model

    def dumps(self, value: BaseModel) -> bytes:
        return value.json().encode()

    def loads(self, data: bytes) -> BaseModel:
        return self._model(**json.loads(data))
