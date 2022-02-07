
import json
from pymonad.either import Left, Right, Either
from cc_backend_lib.errors import http_error
from cc_backend_lib import models
from . import api_client

class SchedulerClient(api_client.ApiClient):
    def deserialize(self, data: bytes) -> Either[http_error.HttpError, models.time_partition.TimePartition]:
        try:
            return Right(models.time_partition.TimePartition(**json.loads(data)))
        except Exception as e:
            return Left(http_error.HttpError(message = str(e), http_code = 500))

    async def time_partition(self, shift: int = 0) -> Either[http_error.HttpError, models.time_partition.TimePartition]:
        response = await self._get(self._path(""), parameters = self._parameters({"shift":shift}))
        return response.then(self.deserialize)
