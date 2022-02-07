
import json
import pydantic
from pymonad.either import Left, Right, Either
from cc_backend_lib import models
from cc_backend_lib.errors import http_error
from . import model_api_client

class PredictionsClient(model_api_client.ModelApiClient[models.prediction.PredictionFeature, models.prediction.PredFeatureCollection]):
    """
    PredictionsClient
    =================

    parameters:
        base_url (str): URL pointing to an API instance
        path (str): Path in API that exposes users = ""

    A client that can be used to fetch predictions from an API.
    """
    def _model_deserialize(self, data: bytes, model: pydantic.BaseModel) -> Either[http_error.HttpError, pydantic.BaseModel]:
        try:
            return Right(model(**json.loads(data)))
        except Exception:
            return Left(http_error.HttpError(http_code = 500, message = "Failed to deserialize item"))

    def deserialize_detail(self, data:bytes)-> Either[http_error.HttpError, models.prediction.PredictionFeature]:
        return self._model_deserialize(data, models.prediction.PredictionFeature)

    def deserialize_list(self, data:bytes)-> Either[http_error.HttpError, models.prediction.PredFeatureCollection]:
        return self._model_deserialize(data, models.prediction.PredFeatureCollection)
